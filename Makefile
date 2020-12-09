# to make the .mpy packge for circuitpython
# and to run tests

# depend on git-controlled files, and their directory to detect dropping a file
heavy_mpy = $(shell git ls-files every | egrep '\.py$$' | egrep -v 'lightweight' | sed 's/\.py$$/.mpy/') 
heavy_dirs = $(shell echo $(heavy_mpy) | xargs dirname | sort -u)
lightweight_mpy = $(shell git ls-files every/lightweight* every/__init__.py | egrep '\.py$$' | sed 's/\.py$$/.mpy/') 
heavy_dirs = $(shell echo $(lightweight_mpy) | xargs dirname | sort -u)

version = $(shell python3 -c 'import every.version; print( every.version.__version__)')

# we want to depend on the mpy-cross command, so we recompile if it updates
mpy_cross_command = $(or $(shell which mpy-cross), mpy-cross)

.PHONY : release
release : every-mpy-$(version).zip every-mpy-lightweight-$(version).zip
	@# extra release artefacts, the mpy .zip files

# what version will we make?
.PHONY : version
version : git-tag-up-to-date
	@echo $(version) every-mpy-$(version).zip every-mpy-lightweight-$(version).zip

# You should: make clean
# for both mpy.zip's, we need the git tag to name it
# for both mpy.zip's, remove old mpy's first, so we don't get excess/old ones
every-mpy-$(version).zip : $(heavy_mpy) $(heavy_dirs) | git-tag-up-to-date
	rm $@ 2>/dev/null || true
	zip $@ $(heavy_mpy)

every-mpy-lightweight-$(version).zip : $(lightweight_mpy) $(heavy_dirs) | git-tag-up-to-date
	rm $@ 2>/dev/null || true
	zip $@ $(lightweight_mpy)

# You can use this if you've made a minor revision (readme, or bug fix):
# commit all changes, then: make minor-release
# It will update the git-tag and do the default make, which is the mpy.zips
.PHONY : minor-release
minor-release : 
	@# increment version and tag and make
	python3 -c 'import every.version; vparts = every.version.__version__.split("."); print("#v",vparts); vparts[-1] = str(int(vparts[-1])+1); print("__version__ = \"%s\"" % ".".join(vparts))' > .x
	cat .x > every/version.py; rm .x
	git commit -a -m 'increment minor version'
	git tag v`python3 -c 'import every.version; print( every.version.__version__)'`
	$(MAKE)

# we want the .mpy to depend on the mpy-cross command too!
%.mpy : %.py $(mpy_cross_command)
	mpy-cross $< -o $@

# tell user that we need mpy-cross
.PHONY : mpy-cross
mpy-cross :
	echo "get, install as mpy-cross, and add to PATH: mpy-cross command from https://pypi.org/project/mpy-cross/"; \
	exit 1; \

.PHONY : git-tag-up-to-date
git-tag-up-to-date :
	@# Check version==git-tag==head
	@if test "$$FORCE" = ""; then \
		if ! git diff-index --quiet HEAD; then \
			git status; \
			echo "Won't make: Uncommited changes (use env FORCE=1 to override)"; \
			exit 1; \
		fi; \
		if test "`git tag --list v$(version)`" = '' ; then \
			echo "No git-tag matching version.py: v$(version). # git tag v$(version) (use env FORCE=1 to override)"; \
			exit 1; \
		fi; \
		if test `set -x; git show-ref -s --tags v$(version)` != `git show-ref --head --heads -s HEAD`; then \
			echo "HEAD != tag v$(version). update version.py (use env FORCE=1 to override)"; \
			exit 1; \
		fi; \
	fi

# just for convenience
# and, it enforces no __pycache__
.PHONY : test tests
test tests : clean $(shell find tests -name '*_tests.py')
	# python3 -m unittest tests.every_tests.PeriodAndDurationTests.testSetInterval
	python3 -m unittest $(shell find tests -name '*_tests.py')

.PHONY : clean
clean :
	find . -name __pycache__ | xargs --no-run-if-empty echo rm -rf 
	find . -name '*.mpy' | xargs --no-run-if-empty rm
	
# just for convenience, we don't commit README.html
.PHONY : doc docs
doc docs : README.html
README.html : README.md
	markdown $^ > $@
