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
