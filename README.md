# 배경

FastAPI는 많은 부분에서 편리합니다.
특히, 요청/응답의 타입 체크도 자동으로 해주는 것과 문서를 자동으로 생성해주는 것이 그렇습니다.

하지만 FastAPI의 방식이 요청의 유형에 따라 응답의 형태가 달라져야하는 경우에는 잘 작동하지 않는 것 같습니다.
이 예제에서는 어떻게하면 요청의 유형에 따라 다른 응답을 제공할 수 있는지 살펴보려고 합니다.

# 예제 실행 방법

특정 파이썬 버전을 사용하기 위해 pyenv를 사용했습니다.
여기서 사용한 버전은 `.python-version`에 들어있습니다.
pyenv를 사용한다면 자동으로 명시된 버전을 사용할 것입니다.

아래 명령어로 virtual environment를 만들어줍니다.

```bash
python -m venv venv
```

그럼 루트 디렉토리에 venv가 생성될 것입니다.
해당 경로의 파이썬을 사용하기 위해 다음 명령어를 사용합니다.

```bash
source venv/bin/activate
```

그럼 이제 해당 경로에 조성된 파이썬 환경을 사용하게 됩니다.
다음 명령어로 필요 패키지를 설치합니다.

```bash
pip install -r requirements.txt
```

설치가 끝나면 다음 명령어로 uvicorn 서버를 실행합니다.

```bash
uvicorn main:app --reload
```

`http://127.0.0.1:8000/docs` 를 웹브라우저로 열고, 내용을 확인하고 요청을 날려보기도 해 봅니다.

# 예제 API 설명

제가 개인적으로 좋아하는 축구선수들로 예제를 만들어봤습니다.
축구선수의 정보를 DB(여기서는 in-memory)에 들고 있다가,
`GET /legends` 요청을 하면 레전드 축구선수 4인의 목록이 나오도록 했습니다.

여기서는 영국 선수들만 나오도록 만들어봤는데요.
이 분들의 프로필을 보다보니 키 정보에 문제가 있습니다.
단위가 피트, 인치로 되어있다는 것인데요.
예를 들어 Steven Gerrard 선수의 키는 6.0 즉, 6 피트 0 인치인 것이죠.
이런 단위 체계를 대영제국에서 쓴다고 하여 "imperial"이라고 부른답니다.

하고 싶은 것은 이렇습니다.
이런 단위 체계가 익숙하신 분은 그 단위 그대로 볼 수 있게 하고요.
저처럼 미터법이 익숙한 사람은 meter 단위로 보게 하는 겁니다.

# 해결 방법

## pydantic class에 OR 사용하기

FastAPI에서는 응답 모델(response_model)을 pydantic 모델로 지정해놓으면 타입 체크는 물론, 문서까지도 만들어줍니다.
이 기능을 사용하면서, 요청 파라미터에 따라 응답의 타입과 값이 달라지도록 만드려고합니다.

우선 사용할 기능은 pydantic의 `|` (OR) 연산자입니다.

```python
class LengthInImperialUnit(BaseModel):
    feet: int = 0
    inch: float = 0

...

class EnglishPlayer(BaseModel):
    name: str
    height: LengthInImperialUnit | float
    position: str
    birth_date: date
    teams: list[TeamId]
```

위의 EnglishPlayer 클래스를 보면 height가 두가지 중 하나의 타입이라고 나옵니다.
`uvicorn main:app --reload` 명령어로 실행하고, 자동 생성된 문서의 스키마를 살펴보면 `anyOf`라는 말과 함께 `LengthInImperialUnit`, `number` 두 종류의 타입이 잘 표시되는 것을 볼 수 있습니다.

## 데이터를 dictionary로 바꾸고, 조건에 따라 내용 다르게 넣고 다시 인스턴스화 하기

문서는 해결됐지만, 실제 데이터를 넣어야 하는 문제가 있습니다.
pydantic을 클래스처럼 생각해서 생성자를 잘 조작하면 되지 않을까 싶어 그렇게 해보았지만 제대로 동작하지 않았습니다.
이 도구는 타입 validater라 일반적인 클래스와는 다른 모양입니다.

좀 지저분하지만 해법을 찾았습니다.
바로 dictionary로 데이터를 바꾼 다음, 조건에 맞게 데이터를 변경하고 다시 인스턴스화 하는 것입니다.
이 내용을 return하면 validater가 체크한 뒤 응답을 보내게 됩니다.

# 결론

더 나은 방법이 있을지 모른다는 생각이 많이 듭니다만, 일을 더 복잡하게 만드는 것 같습니다.
일단 이 방법을 사용하면 동작은 하니까... 당장은 만족하도록 하겠습니다.
물러날 때를 알아야죠!
