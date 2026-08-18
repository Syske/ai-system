## [Spring] Bean Loading Issue

Date: 2026-07-06

Priority: P1

Context:

Spring Boot multi module project.


Problem:

Component scanning missed new package.


Root Cause:

Package structure changed.


Solution:

Verify:

- @ComponentScan
- starter configuration
- module dependency


Lesson:

Adding a Spring component requires checking startup scanning.


Scope:

- Spring Boot multi-module projects
- New package / new component registration

## [Spring] ThreadPoolTaskExecutor Unbounded Queue Disables maxPoolSize

Date: 2026-08-18

Priority: P1

Context:

user-center-api TaskExecutorConfiguration defines syncAuthTaskExecutor as a Spring
ThreadPoolTaskExecutor with corePoolSize=8, maxPoolSize=100 and
queueCapacity=Integer.MAX_VALUE (unbounded). It is used for per-enterprise async
user-auth full sync (AuthSyncService, UserElasticsearchConsistencyListener).

Problem:

Assumed maxPoolSize=100 bounded thread growth, but real concurrency never exceeded
8 threads. ThreadPoolExecutor only spawns beyond corePoolSize when the queue is
full; an unbounded queue means the pool never grows and tasks pile up in memory
(OOM risk for heavy full-sync tasks), while maxPoolSize stays dead config.

Root Cause:

JDK ThreadPoolExecutor semantics: execute() queues first; queue capacity reached
only then do new threads spin up to max. queueCapacity=Integer.MAX_VALUE makes the
queue effectively never full.

Solution:

Use a bounded queueCapacity when maxPoolSize is meant to be effective; treat
maxPoolSize under an unbounded queue as corePoolSize-only. When bounding the queue,
also choose and document the RejectedExecutionHandler (AbortPolicy default throws
TaskRejectedException at execute() — call sites without try/catch silently stop
submitting remaining items).

Lesson:

For Spring ThreadPoolTaskExecutor, an unbounded queue (Integer.MAX_VALUE) makes
maxPoolSize ineffective — actual concurrency equals corePoolSize and load moves
into unbounded memory; bound the queue (or accept core-only behavior) and handle
rejection at submit sites.

Scope:

- Spring ThreadPoolTaskExecutor configuration
- user-center-api TaskExecutorConfiguration / AuthSyncService / UserElasticsearchConsistencyListener
- Any async batch sync using "one task per entity" submission

Related:

- Standard: governance/standards/ (concurrency/thread-pool guidance if any)
