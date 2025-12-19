OctoFit Java module — Maven scaffold (Java 17)

This folder contains a minimal Maven project configured for Java 17.

Build and run (Ubuntu / Linux):

Install OpenJDK 17 via apt:

```bash
sudo apt update
sudo apt install -y openjdk-17-jdk maven
```

Or install via SDKMAN (recommended for per-user toolchains):

```bash
curl -s "https://get.sdkman.io" | bash
source "$HOME/.sdkman/bin/sdkman-init.sh"
sdk install java 17.0.8-tem
sdk install maven
```

Build the project:

```bash
mvn -f octofit-tracker/java/pom.xml clean package
```

Run the app:

```bash
java -jar octofit-tracker/java/target/octofit-java-0.1.0.jar
```

Notes:
- The `pom.xml` targets Java 17. Ensure your `java -version` reports a 17 runtime.
- If you prefer Gradle, I can scaffold a Gradle build instead.
