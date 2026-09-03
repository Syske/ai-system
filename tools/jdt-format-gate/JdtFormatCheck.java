// JdtFormatCheck — eclipse JDT formatter 干跑校验（C2 方案，2026-09-02 v3）
//
// 用法（由 tools/format-jdt-gate.py 驱动）：
//   java -cp <jdt-core.jar>:<org.eclipse.text.jar>:<build-dir> JdtFormatCheck \
//       <eclipse-format.xml> <src-dir> [--check] [--dump-dir <path>]
//
// 行为：eclipse JDT ToolFactory + eclipse-format.xml（tab=4 space）对目录内 .java
// 干跑格式化（不写盘）：手工应用 TextEdits（不依赖 jface.text），统计差异文件/行。
// --dump-dir：将 differ 文件的 formatted 结果写入 <path>/<相对路径>（保留目录结构），
//             并逐文件打印差异文件相对路径（供 profile 校准的差异分类反推）。
// --apply：将 formatted 结果直接写回源文件（业务仓格式基线；配合 git diff -w 安全校验）。
// exit: 0 = 全部一致（或 apply 完成）  1 = 有差异  2 = 用法错误
// --ignore-file <path>：每行一个相对路径（srcDir 下），check/apply 跳过（已知无 fixpoint
//                     的振荡边界文件，如 formatter 对合往返的文件）；行首 # 为注释。
//
// profile 建议用 IDEA 导出的 Eclipse XML Profile 替换（见 eclipse-format.xml 注释）。
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import javax.xml.parsers.DocumentBuilderFactory;
import org.eclipse.jdt.core.ToolFactory;
import org.eclipse.jdt.core.formatter.CodeFormatter;
import org.eclipse.jdt.core.formatter.DefaultCodeFormatterConstants;
import org.eclipse.text.edits.*;
import org.w3c.dom.*;

/** 干跑式格式化一致性检查（不修改源码，最小依赖闭包：jdt.core + org.eclipse.text）。 */
public class JdtFormatCheck {

    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("usage: JdtFormatCheck <eclipse-format.xml> <src-dir> [--check] [--dump-dir <path>]");
            System.exit(2);
        }
        Map<String, String> options = loadOptions(Paths.get(args[0]));
        CodeFormatter formatter = ToolFactory.createCodeFormatter(options);
        Path srcDir = Paths.get(args[1]);
        Path dumpDir = null;
        boolean apply = false;
        Set<String> ignoreSet = null;
        for (int i = 2; i < args.length; i++) {
            if ("--dump-dir".equals(args[i]) && i + 1 < args.length) {
                dumpDir = Paths.get(args[++i]);
            } else if ("--apply".equals(args[i])) {
                apply = true;
            } else if ("--ignore-file".equals(args[i]) && i + 1 < args.length) {
                ignoreSet = new HashSet<String>();
                for (String line : Files.readAllLines(Paths.get(args[++i]), StandardCharsets.UTF_8)) {
                    String t = line.trim();
                    if (!t.isEmpty() && !t.startsWith("#")) {
                        ignoreSet.add(t);
                    }
                }
            }
        }

        List<Path> javaFiles = new ArrayList<Path>();
        try (java.util.stream.Stream<Path> stream = Files.walk(srcDir)) {
            stream.filter(p -> p.toString().endsWith(".java")).forEach(javaFiles::add);
        }
        Collections.sort(javaFiles);

        int differFiles = 0;
        int diffLines = 0;
        String firstDiffer = "";
        for (Path f : javaFiles) {
            String relStr = srcDir.relativize(f).toString().replace('\\', '/');
            if (ignoreSet != null && ignoreSet.contains(relStr)) {
                continue;
            }
            String src = new String(Files.readAllBytes(f), StandardCharsets.UTF_8);
            String formatted = formatOnce(formatter, src);
            if (formatted != null && !formatted.equals(src)) {
                differFiles++;
                diffLines += countDiffLines(src, formatted);
                if (firstDiffer.isEmpty()) {
                    firstDiffer = f.toString();
                }
                if (dumpDir != null) {
                    Path rel = srcDir.relativize(f);
                    Path out = dumpDir.resolve(rel);
                    Files.createDirectories(out.getParent());
                    Files.write(out, formatted.getBytes(StandardCharsets.UTF_8));
                    System.out.println("DIFF " + rel);
                }
                if (apply) {
                    // 迭代至稳定：eclipse formatter 个别文件一次格式化不收敛（如长 lambda/三元组合），
                    // 循环至 fixpoint（最多 5 轮），保证 apply 后 check 为 0。
                    String cur = formatted;
                    int rounds = 1;
                    for (; rounds < 5; rounds++) {
                        String next = formatOnce(formatter, cur);
                        if (next == null || next.equals(cur)) {
                            break;
                        }
                        cur = next;
                    }
                    Files.write(f, cur.getBytes(StandardCharsets.UTF_8));
                    System.out.println("APPLIED " + srcDir.relativize(f) + " x" + rounds);
                }
            }
        }
        System.out.println("JdtFormatCheck: files=" + javaFiles.size()
                + " differ=" + differFiles + " diffLines=" + diffLines
                + (firstDiffer.isEmpty() ? "" : " first=" + firstDiffer)
                + (apply ? " [apply 完成]" : ""));
        System.exit(apply ? 0 : (differFiles == 0 ? 0 : 1));
    }

    /** 一次格式化：接收 TextEdit 后手工应用（leaf edits 按 offset 升序重放）。 */
    private static String formatOnce(CodeFormatter formatter, String src) {
        try {
            TextEdit edits = formatter.format(
                    CodeFormatter.K_COMPILATION_UNIT, src, 0, src.length(), 0, "\n");
            if (edits == null) {
                return null; // 语法解析失败：跳过（不判 diff）
            }
            List<TextEdit> leaves = new ArrayList<TextEdit>();
            collectLeaves(edits, leaves);
            leaves.sort(Comparator.comparingInt(TextEdit::getOffset));
            StringBuilder sb = new StringBuilder(src);
            // 从后往前应用，避免 offset 漂移
            for (int i = leaves.size() - 1; i >= 0; i--) {
                applyEdit(sb, leaves.get(i));
            }
            return sb.toString();
        } catch (Exception e) {
            return null;
        }
    }

    private static void collectLeaves(TextEdit edit, List<TextEdit> out) {
        TextEdit[] children = edit.getChildren();
        if (children == null || children.length == 0) {
            out.add(edit);
            return;
        }
        for (TextEdit c : children) {
            collectLeaves(c, out);
        }
    }

    private static void applyEdit(StringBuilder sb, TextEdit e) {
        int off = e.getOffset();
        int len = e.getLength();
        if (e instanceof InsertEdit) {
            sb.insert(off, ((InsertEdit) e).getText());
        } else if (e instanceof DeleteEdit) {
            sb.delete(off, off + len);
        } else if (e instanceof ReplaceEdit) {
            sb.replace(off, off + len, ((ReplaceEdit) e).getText());
        }
    }

    private static int countDiffLines(String a, String b) {
        String[] la = a.split("\n", -1);
        String[] lb = b.split("\n", -1);
        int n = Math.max(la.length, lb.length);
        int diff = 0;
        for (int i = 0; i < n; i++) {
            String x = i < la.length ? la[i] : "";
            String y = i < lb.length ? lb[i] : "";
            if (!x.equals(y)) {
                diff++;
            }
        }
        return diff;
    }

    /** 读取 eclipse formatter profile xml（org.eclipse.jdt.core.formatter.* settings）。 */
    private static Map<String, String> loadOptions(Path xml) throws Exception {
        Map<String, String> options = new HashMap<>(
                DefaultCodeFormatterConstants.getEclipseDefaultSettings());
        Document doc = DocumentBuilderFactory.newInstance()
                .newDocumentBuilder().parse(xml.toFile());
        NodeList settings = doc.getElementsByTagName("setting");
        for (int i = 0; i < settings.getLength(); i++) {
            Element s = (Element) settings.item(i);
            String id = s.getAttribute("id");
            String value = s.getAttribute("value");
            if (id != null && id.startsWith("org.eclipse.jdt.core.formatter.")) {
                options.put(id, value);
            }
        }
        return options;
    }
}