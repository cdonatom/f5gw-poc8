git clone https://github.com/srsLTE/srsLTE.git
cd srsLTE
git checkout 47a1880ab1beb596c49ccc006ad5ff7a5be90429
git apply ../lte_subframe.patch
rm -r build
mkdir build
cd build
cmake ../
make
