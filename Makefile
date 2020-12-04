# to make the .mpy packge for circuitpython

# depend on git-controlled files, and their directory to detect dropping a file

all_mpy = $(shell git ls-files | egrep '\.py$$' | sed 's/\.py$$/.mpy/') 
all_py = $(shell git ls-files | egrep '\.py$$') 
all_dirs = $(shell git ls-files | xargs dirname | sort -u)
every-mpy.zip : $(all_mpy) $(all_dirs)
	echo "MAKE " $(all_mpy)
	# [ -e $@ ] && rm $@
	rm $@ 2>/dev/null || true
	zip $@ $(all_mpy)

%.mpy : %.py
	@ if ! which mpy-cross >/dev/null; then \
		echo "get, install as mpy-cross, and add to PATH: mpy-cross command from https://pypi.org/project/mpy-cross/"; \
		exit 1; \
	fi
	mpy-cross $< -o $@
