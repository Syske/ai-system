## [Spring] Bean Loading Issue


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