# 1단계: Gradle로 Spring Boot 실행 JAR 빌드
FROM eclipse-temurin:21-jdk AS builder

WORKDIR /workspace

COPY gradlew ./
COPY gradle ./gradle
COPY settings.gradle ./
COPY build.gradle ./

RUN chmod +x ./gradlew

COPY src ./src

RUN ./gradlew clean bootJar \
    --no-daemon \
    --no-configuration-cache


# 2단계: 실행 이미지
FROM eclipse-temurin:21-jre

WORKDIR /app

RUN groupadd --system spring \
    && useradd --system \
        --gid spring \
        --create-home \
        spring

COPY --from=builder \
    /workspace/build/libs/*.jar \
    /app/application.jar

RUN chown spring:spring /app/application.jar

USER spring:spring

EXPOSE 9999

ENTRYPOINT ["java", "-XX:MaxRAMPercentage=75.0", "-Djava.security.egd=file:/dev/./urandom", "-jar", "/app/application.jar"]

## Docker Only 실행 가이드


## 1단계 : 이미지 빌드
# docker build -t loginauth-extended-app .
# docker images
# 이미지는 프로젝트 폴더에 파일로 생기는 게 아니라, 도커 데몬(Docker daemon)이 관리하는 별도의 내부 저장소에 저장
# 생성된 이미지 파일을 밖으로 빼고 싶다면
# docker save -o loginauth-extended-app.tar loginauth-extended-app


## 2단계 : 컨테이너 실행
# docker run -d \
#   --name loginauth-extended-app \
#   --restart unless-stopped \
#   -p 9999:9999 \
#   -e DB_URL="jdbc:mariadb://host.docker.internal:3379/sql_db" \
#   -e DB_USER="root" \
#   -e DB_PASSWORD="SqlDba-1" \
#   -e COOKIE_SECURE="false" \
#   -e JWT_SECRET="change-this-development-secret-key-at-least-32-characters" \
#   -e JWT_ISSUER="loginauth-board-advanced" \
#   -e JWT_ACCESS_TOKEN_TTL="1h" \
#   -e TZ="Asia/Seoul" \
#   --add-host host.docker.internal:host-gateway \
#   loginauth-extended-app


##   --add-host host.docker.internal:host-gateway \
# 컨테이너 안에서 리눅스 호스트 자체를 가리킬 수 있도록 /etc/hosts에 항목을 추가해주는 옵션 (맥북/윈도우 개발 > 리눅스 배포 가능)

# 컨테이너 → 인터넷(외부 IP) : 이건 원래부터 기본으로 가능합니다. 도커가 컨테이너를 만들 때 자동으로 NAT/게이트웨이를 설정해서, 별도 설정 없이도 컨테이너 안에서 curl google.com 가능합니다.
# 컨테이너 → 자신을 실행 중인 호스트 머신 : 이건 원래 안 되거나 애매합니다. 컨테이너 입장에서 "나를 실행시킨 이 호스트 자체"를 가리키는 이름이 기본적으로 없기 때문입니다. --add-host ...host-gateway는 바로 이 경우를 위한 설정입니다.


## 컨테이너 접속
# docker exec -it loginauth-extended-app /bin/sh


## 환경변수 확인
# env | grep -E 'DB_|JWT_|TZ'


## 네트워크 확인
# getent hosts host.docker.internal


## 앱 프로세스 확인
# ps aux


## 앱이 떠 있는지 체크
# curl -v http://localhost:9999/actuator/health
# 또는 실제 존재하는 엔드포인트로


## 컨테이너 안에 없는 도구 없이, 호스트에서 컨테이너 내부 상태를 확인
# $ exit                                         # 컨테이너에서 빠져 나오기
# docker logs -f loginauth-extended-app          # 앱 로그 실시간 확인
# docker stats loginauth-extended-app            # 리소스 사용량
# docker inspect loginauth-extended-app          # 네트워크/환경변수 등 상세 정보


## 3단계 : 컨테이너 중지/삭제
# docker stop loginauth-extended-app
# docker rm loginauth-extended-app
# docker rmi loginauth-extended-app