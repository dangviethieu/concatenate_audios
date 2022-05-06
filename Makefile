SRC_FOLDER := $(shell pwd)

install:
	pip install -r requirements.txt

run:
	python main.py

gen_spec:
	pyi-makespec --onefile --noconsole --name fbcomment --icon icon.ico --hiddenimport "engineio.async_drivers.threading" --hiddenimport "sqlalchemy.ext.baked" main.py

gen_win64:
	docker run -it --rm -v "${SRC_FOLDER}:/src/" --entrypoint /bin/sh cdrx/pyinstaller-windows -c \
"apt-get update -y && \
 apt-get install -y git && \
 git clone --depth 1 --branch v0.32 https://github.com/samuelcolvin/pydantic.git /wine/drive_c/pydantic && \
 pip install -e /wine/drive_c/pydantic && \
 python -m pip install --upgrade pip && \
 /entrypoint.sh"

zip:
	cd dist/windows && zip -r fbcomment.zip fbcomment.exe icon.ico chromedriver.exe