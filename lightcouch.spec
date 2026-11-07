Name:		lightcouch
Version:	0.2.0
Release:	1
Summary:	CouchDB Java API
Group:		Databases
License:	ASL 2.0
URL:		https://github.com/lightcouch/LightCouch
Source0:	https://github.com/lightcouch/LightCouch/archive/refs/tags/lightcouch-%{version}.tar.gz#/lightcouch-%{version}.tar.gz

BuildArch:	noarch
BuildRequires:	python
# Literal, so the first rpmbuild -bs records them before sysjar is installed.
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildRequires:	mvn(org.apache.httpcomponents:httpclient)
# The httpclient POM parents httpcomponents-client in the same package.
# That parent POM parents httpcomponents-parent, which is a separate package.
BuildRequires:	mvn(org.apache.httpcomponents:httpcomponents-parent:pom::)
# httpcomponents-parent and commons-parent both parent apache.
BuildRequires:	mvn(org.apache:apache:pom::)
BuildRequires:	mvn(commons-codec:commons-codec)
BuildRequires:	mvn(commons-logging:commons-logging)
# Codec and logging parent commons-parent. A parent POM is not a Requires.
BuildRequires:	mvn(org.apache.commons:commons-parent:pom::)
BuildRequires:	mvn(com.google.code.gson:gson)
BuildSystem:	maven
BuildOption(install):	--file-name lightcouch

Obsoletes:	%{name}-javadoc < %{version}-%{release}

%description
LightCouch is a Java client for CouchDB. 0.2.0 is the last upstream
release. It speaks CouchDB 2: Mango _find queries, string update
sequences, and bulk documents with new_edits. Temp views and
all_or_nothing bulk updates are gone. The client is Closeable and
reads view documents as UTF-8. This build uses the system HttpClient
4.5, Gson, Commons Codec, and Commons Logging jars. The sources import
Codec and Logging, and Logging is not pulled in by HttpClient, so
both are direct dependencies. The compiler release is 8. The DocBook
guide and the tests are left out.

%prep
%autosetup -n LightCouch-lightcouch-%{version}
rm -rf guide src/test
find . -name '*.jar' -delete
python - <<'PY'
from pathlib import Path

if Path("guide").exists() or Path("src/test").exists():
    raise SystemExit("guide or tests remain")
java_files = list(Path("src/main/java").rglob("*.java"))
if len(java_files) != 27:
    raise SystemExit("java files " + str(len(java_files)))
if list(Path(".").rglob("*.jar")):
    raise SystemExit("prebuilt jar remains")
for pom in Path(".").rglob("pom.xml"):
    pom.unlink()

Path("pom.xml").write_text("""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.lightcouch</groupId>
  <artifactId>lightcouch</artifactId>
  <version>%{version}</version>
  <packaging>jar</packaging>
  <name>LightCouch</name>
  <description>CouchDB Java API. Built against the system HttpClient, Gson, Codec, and Logging jars.</description>
  <url>https://github.com/lightcouch/LightCouch</url>
  <licenses>
    <license>
      <name>Apache License, Version 2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
    </license>
  </licenses>
  <properties>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <maven.compiler.release>8</maven.compiler.release>
  </properties>
  <dependencies>
    <dependency>
      <groupId>org.apache.httpcomponents</groupId>
      <artifactId>httpclient</artifactId>
      <version>4.5.14</version>
    </dependency>
    <dependency>
      <groupId>com.google.code.gson</groupId>
      <artifactId>gson</artifactId>
      <version>2.15.0</version>
    </dependency>
    <dependency>
      <groupId>commons-codec</groupId>
      <artifactId>commons-codec</artifactId>
      <version>1.23.0</version>
    </dependency>
    <dependency>
      <groupId>commons-logging</groupId>
      <artifactId>commons-logging</artifactId>
      <version>1.4.0</version>
    </dependency>
  </dependencies>
  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-compiler-plugin</artifactId>
        <version>3.12.1</version>
        <configuration>
          <release>8</release>
        </configuration>
      </plugin>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-jar-plugin</artifactId>
        <version>3.3.0</version>
      </plugin>
    </plugins>
  </build>
</project>
""", encoding="utf-8")
pom = Path("pom.xml").read_text(encoding="utf-8")
poms = sorted(str(path) for path in Path(".").rglob("pom.xml"))
if poms != ["pom.xml"]:
    raise SystemExit("poms " + str(poms))
for needle in (
    "<artifactId>lightcouch</artifactId>",
    "<artifactId>httpclient</artifactId>",
    "<artifactId>gson</artifactId>",
    "<artifactId>commons-codec</artifactId>",
    "<artifactId>commons-logging</artifactId>",
    "<version>4.5.14</version>",
    "<version>2.15.0</version>",
    "<version>1.23.0</version>",
    "<version>1.4.0</version>",
    "<version>%{version}</version>",
    "<release>8</release>",
    "<maven.compiler.release>8</maven.compiler.release>",
):
    if needle not in pom:
        raise SystemExit("pom missing " + needle)
for needle in ("junit", "oss-parent", "SNAPSHOT", "<source>", "<target>", "<parent>"):
    if needle in pom:
        raise SystemExit("pom still contains " + needle)
PY

%build -a
java --module-path target/lightcouch-%{version}.jar --describe-module lightcouch > module-describe.txt
# A versioned jar prints "name@version ... automatic", not "name automatic".
grep -q '^lightcouch' module-describe.txt || { cat module-describe.txt; exit 1; }
grep -q ' automatic$' module-describe.txt || { cat module-describe.txt; exit 1; }

%files -f .mfiles
%doc LICENSE README.md
