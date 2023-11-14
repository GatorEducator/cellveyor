# 💫 cellveyor

[![build](https://github.com/gkapfham/cellveyor/actions/workflows/build.yml/badge.svg)](https://https://github.com/gkapfham/cellveyor/actions/workflows/build.yml)
[![Language:Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://github.com/gkapfham/cellveyor/search?l=python)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-Yes-blue.svg)](https://github.com/gkapfham/cellveyor/graphs/commit-activity)

## 🎉 Introduction

- **Cellveyor** is a python program that uses

## 😂 Definitions


## 🔋Features


## ⚡️ Requirements


## 🔽 Installation


## 🐋 Docker


## 🪂 Configuration


## ✨ Analysis


## 🚧 Integration


## 🌄 Results


## 🌎 Deployment


## 🤯 Interaction


## 📊Log


## 🤗 Learning


## Example Command

```
poetry run cellveyor --spreadsheet-directory \
--spreadsheet-file <Spreadsheet Filename> \
--sheet-name <Sheet Name> \
--key-attribute "<Key Attribute Name>" \
--key-value "<Key Value>" \
--column-regexp "<Column Regular Expression>" \
--feedback-regexp "<Feedback Column Regular Expression>" \
--feedback-file <Path to General Feedback File> \
--feedback-file <Path to Specific Feedback File> \
--github-token <Private GitHub Access Token> \
--github-organization <GitHub Organization Name> \
--github-repository-prefix <Repository Prefix> \
--transfer-report
```

### Other Example Command

```
poetry run cellveyor --spreadsheet-directory \
/home/gkapfham/working/data/gradebook/2023
--spreadsheet-file CMPSC-203-Fall-2023-Gradebook.xlsx \
--sheet-name Main \
--key-attribute "Student GitHub" \
--key-value "gkapfham" \
--column-regexp "^(Summary Grade|Final Grade) .*$" \
--feedback-regexp "Summary Grade 1 - Feedback" \
--feedback-file /home/gkapfham/working/teaching/github-classroom
/feedback/all/feedback.yml \
--feedback-file /home/gkapfham/working/teaching/github-classroom
/feedback/developer-development/feedback-overall-course-assessment.yml \
--github-token <Private GitHub Acess Token> \
--github-organization Allegheny-Computer-Science-203-F2023 \
--github-repository-prefix computer-science-203-fall-2023-course-assessment \
--transfer-report
```

