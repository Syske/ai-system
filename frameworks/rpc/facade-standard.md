# RPC Facade Standard

## Request

All facade request objects MUST extend:

net.coolcollege.platform.util.model.BaseRequest

Example:

public class XxxRequest extends BaseRequest {

}

---

## Result

All facade result objects MUST extend:

net.coolcollege.platform.util.model.BaseResult

Example:

public class XxxResult extends BaseResult {

}

---

## Interface

Facade interfaces MUST use:

BaseRequest subclasses as parameters.

BaseResult subclasses as return types.

---

## Never

Do not use:

- POJO as Request
- POJO as Result
- Map
- Object
- List directly

except explicitly approved by architecture.