#!/bin/bash
# $WORKSPACE is set from jenkins.
# When running from project root manually, use:

# environment settings.
WORKSPACE=${WORKSPACE-`pwd`}
PYBIN=`which python2.7`
## PYTHONPATH
if [[ $1 == "local" ]]; then
  export PYTHONPATH=$WORKSPACE:$OLD_PYTHONPATH
else
  OLD_PYTHONPATH=$PYTHONPATH
  export PYTHONPATH=$WORKSPACE:$OLD_PYTHONPATH
  scvar=`$PYBIN -c 'import solvcon; print solvcon.__version__'`
  export PYTHONPATH=$WORKSPACE/dist/SOLVCON-$scvar:$OLD_PYTHONPATH
  unset OLD_PYTHONPATH scvar
fi
## example home.
EXHOME=$WORKSPACE/examples/linear/cvg
RESULTDIR=$EXHOME/result
## initialize return value (no error).
retval=0

# change to location and clear left-overs.
cd $EXHOME
rm -rf $RESULTDIR

# 2D.
cmd="$PYBIN go run cvg2d_200 cvg2d_150 cvg2d_100 cvg2d_50"
echo $cmd
$cmd
lret=$?; if [[ $lret != 0 ]] ; then retval=$lret; fi

# print converge.
cmd="$PYBIN go converge cvg2d --order=2 --order-tolerance=0.5 --stop-on-over"
echo $cmd
$cmd
lret=$?; if [[ $lret != 0 ]] ; then retval=$lret; fi

exit $retval
