FROM maven:3.5-jdk-8 AS build

WORKDIR /fmap-server

COPY ./fmap-server/pom.xml .
RUN mvn -f ./pom.xml verify clean

COPY ./fmap-server/ .
RUN mvn -f ./pom.xml package

FROM openjdk:8-jre-alpine

WORKDIR /fmap-server

COPY --from=build /fmap-server/target/fmap-server-fmap-server-1.0.jar .
COPY ../fmdata /fmap-server/Resources

CMD ["java", "-cp", "fmap-server-fmap-server-1.0.jar", "ita.triglie.FMapServerStream"]