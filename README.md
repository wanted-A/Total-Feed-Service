<!-- <div align="center"> -->

# 🪄 Total-Feed-service
해시태그로 sns상의 정보들을 조회하고 통계를 조회할 수 있는 서비스

<br>

## Skills
로컬환경
언어 및 프레임워크 : ![Python](https://img.shields.io/badge/Python-3776AB.svg?style=for-the-badge&logo=python&logoColor=white) &nbsp;
![Django](https://img.shields.io/badge/Django-092E20.svg?style=for-the-badge&logo=Django&logoColor=white)

---

## Installation 

```py
pip install -r requirements.txt
```

- https://djecrety.ir/ 에서 django secret_key 생성 후 .env/SECRET_KEY에 복사
```py
SECRET_KEY="secret-key"
```
---

## API Reference

[API 문서](https://ssu-uky.notion.site/API-Docs-0fd0f7b85a934d32b7c912ce8bb2ea8b)


| description | method | url | permission |
| ---- | ---- | ---- | ----|
| 회원가입 | `POST` | /api/v1/users/register/ | `AllowAny` |
| 로그인 | `POST` | /api/v1/users/login/ | `AllowAny` |
| 로그아웃 | `POST` | /api/v1/users/logout/ | `IsAuthenticated` |
| 게시글 목록 조회 | `GET` | /api/v1/boards/?query_params | `AllowAny` |
| 게시글 작성 | `POST` | /api/v1/boards/write/ | `IsAuthenticated` |
| 특정 게시글 조회 | `GET` | /api/v1/boards/<content_id>/ | `IsAuthenticated` |
| 특정 게시글 좋아요(취소 가능) | `POST` | /api/v1/boards/<content_id>/ | `IsAuthenticated` |
| 특정 게시글 수정 | `PUT` | /api/v1/boards/<content_id>/ | `IsAuthenticated` |
| 특정 게시글 삭제 | `DELETE` | /api/v1/boards/<content_id>/ | `IsAuthenticated` |
| 특정 게시글 url로 좋아요 증가(무제한)| `GET`| api/v1/likes/<content_id>/ | `AllowAny` |
| 특정 게시글 공유 | `GET` | api/v1/share/<content_id>/ | `IsAuthenticated` |
| 통계 | `GET` | api/v1/boards/analytics/?query_params | `IsAuthenticated` |

<content_id> = int:content_id

---

## 프로젝트 진행 및 이슈 관리
[![Notion](https://img.shields.io/badge/Notion-%23000000.svg?style=for-the-badge&logo=notion&logoColor=white)](https://ssu-uky.notion.site/ssu-uky/Team-A-c365d2c6babf4d5494b108fa66b39c1f)

---

## Authors
- [이수현](https://github.com/ssu-uky)
- [전정헌](https://github.com/allen9535)
- [윤기연](https://github.com/kyeon06)
- [김종완](https://github.com/mireu-san)
