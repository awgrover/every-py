# to make the .mpy packge for circuitpython

# depend on git-controlled files, and their directory to detect dropping a file
all_mpy = $(shell git ls-files every | egrep '\.py$$' | sed 's/\.py$$/.mpy/') 
all_lightweight_mpy = $(shell git ls-files every/lightweight | egrep '\.py$$' | sed 's/\.py$$/.mpy/') 
all_dirs = $(shell git ls-files | xargs dirname | sort -u)
version = $(shell python3 -c 'import every.version; print( every.version.__version__)')

.PHONY : release
release : every-mpy-$(version).zip every-mpy-lightweight-$(version).zip
	@# extra release artefacts, the mpy .zip files

every-mpy-$(version).zip : $(all_mpy) $(all_dirs) | git-tag-up-to-date
	rm $@ 2>/dev/null || true
	zip $@ $(all_mpy)

every-mpy-lightweight-$(version).zip : $(all_lightweight_mpy) $(all_dirs) | git-tag-up-to-date
	rm $@ 2>/dev/null || true
	zip $@ $(all_lightweight_mpy)

.PHONY : minor-release
minor-release : 
	@# increment version and tag and make
	python3 -c 'import every.version; vparts = every.version.__version__.split("."); print("#v",vparts); vparts[-1] = str(int(vparts[-1])+1); print("__version__ = \"%s\"" % ".".join(vparts))' > .x
	cat .x > every/version.py; rm .x
	git commit -a -m 'increment minor version'
	git tag v`python3 -c 'import every.version; print( every.version.__version__)'`
	$(MAKE)

%.mpy : %.py | mpy-cross
	mpy-cross $< -o $@

.PHONY : mpy-cross
mpy-cross :
	@# check for the mpy-cross tool
	@ if ! which mpy-cross >/dev/null; then \
		echo "get, install as mpy-cross, and add to PATH: mpy-cross command from https://pypi.org/project/mpy-cross/"; \
		exit 1; \
	fi

.PHONY : git-tag-up-to-date
git-tag-up-to-date :
	@# Check version==git-tag==head
	@if test "$$FORCE" = ""; then \
		if ! git diff-index --quiet HEAD; then \
			git status; \
			echo "Won't make: Uncommited changes"; \
			exit 1; \
		fi; \
		if test "`git tag --list v$(version)`" = '' ; then \
			echo "No git-tag matching version.py: v$(version). # git tag v$(version)"; \
			exit 1; \
		fi; \
		if test `set -x; git show-ref -s --tags v$(version)` != `git show-ref --head --heads -s HEAD`; then \
			echo "HEAD != tag v$(version). update version.py"; \
			exit 1; \
		fi; \
	fi
