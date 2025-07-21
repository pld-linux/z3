#
# Conditional build:
%bcond_without	apidocs		# Doxygen documentation
%bcond_with	dotnet		# .NET API (requires MS .NET SDK + mono)
%bcond_without	ocaml		# OCaml API
%bcond_without	ocaml_opt	# native optimized binaries (bytecode is always built)
%bcond_without	python2		# Python2 modules
%bcond_with	sse2		# SSE2 instructions

# not yet available on x32 (ocaml 4.02.1), update when upstream will support it
%ifnarch %{ix86} %{x8664} %{arm} aarch64 ppc sparc sparcv9
%undefine	with_ocaml_opt
%endif
%ifarch %{x8664} x32 pentium4
%define		with_sse2	1
%endif

%{?use_default_jdk}

Summary:	High-performance theorem prover developed at Microsoft Research
Summary(pl.UTF-8):	Wydajne narzędzie do dowodzenia twierdzeń tworzone przez Microsoft Research
Name:		z3
Version:	4.15.2
Release:	1
License:	MIT
Group:		Applications/Engineering
#Source0Download: https://github.com/Z3Prover/z3/releases
Source0:	https://github.com/Z3Prover/z3/archive/z3-%{version}.tar.gz
# Source0-md5:	edce98c601844cd0883d9f552ba8232c
Patch0:		%{name}-pld.patch
Patch1:		%{name}-sse.patch
URL:		https://github.com/Z3Prover/z3
BuildRequires:	cmake >= 3.16
%{?with_apidocs:BuildRequires:	doxygen}
BuildRequires:	gmp-devel
BuildRequires:	gmp-c++-devel
%buildrequires_jdk
%{?use_jdk:BuildRequires:	%{use_jdk}-jre-base-X11}
BuildRequires:	libgomp-devel
# C++20
BuildRequires:	libstdc++-devel >= 6:8
%{?with_dotnet:BuildRequires:	mono-devel}
%if %{with ocaml}
BuildRequires:	ocaml
BuildRequires:	ocaml-findlib
BuildRequires:	ocaml-zarith-devel
%endif
%if %{with python2}
BuildRequires:	python >= 1:2.7
BuildRequires:	python-modules >= 1:2.7
%endif
BuildRequires:	python3 >= 1:3.2
BuildRequires:	python3-modules >= 1:3.2
BuildRequires:	rpm-build >= 4.6
BuildRequires:	rpmbuild(macros) >= 2.021
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Z3 is a high-performance theorem prover being developed at Microsoft
Research.

%description -l pl
Z3 to wydajne narzędzie do dowodzenia twierdzeń tworzone przez
Microsoft Research.

%package devel
Summary:	Development files for Z3
Summary(pl.UTF-8):	Pliki programistyczne Z3
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
Development files for Z3.

%description devel -l pl.UTF-8
Pliki programistyczne Z3.

%package apidocs
Summary:	API documentation for Z3 library
Summary(pl.UTF-8):	Dokumentacja API Biblioteki Z3
Group:		Documentation
BuildArch:	noarch

%description apidocs
API documentation for Z3 library.

%description apidocs -l pl.UTF-8
Dokumentacja API Biblioteki Z3.

%package -n java-z3
Summary:	Java API for Z3 library
Summary(pl.UTF-8):	API języka Java do biblioteki Z3
Group:		Libraries/Java
Requires:	%{name} = %{version}-%{release}

%description -n java-z3
Java API for Z3 theorem prover library.

%description -n java-z3 -l pl.UTF-8
API języka Java do biblioteki dowodzenia twierdzeń Z3.

%package -n ocaml-z3
Summary:	Z3 binding for OCaml
Summary(pl.UTF-8):	Wiązania Z3 dla OCamla
Group:		Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	ocaml-zarith
%requires_eq	ocaml-runtime

%description -n ocaml-z3
This package contains files needed to run bytecode executables using
Z3 library.

%description -n ocaml-z3 -l pl.UTF-8
Pakiet ten zawiera binaria potrzebne do uruchamiania programów
używających biblioteki Z3.

%package -n ocaml-z3-devel
Summary:	Z3 binding for OCaml - development part
Summary(pl.UTF-8):	Wiązania Z3 dla OCamla - cześć programistyczna
Group:		Development/Libraries
Requires:	ocaml-z3 = %{version}-%{release}
Requires:	ocaml-zarith-devel
%requires_eq	ocaml

%description -n ocaml-z3-devel
This package contains files needed to develop OCaml programs using Z3
library.

%description -n ocaml-z3-devel -l pl.UTF-8
Pakiet ten zawiera pliki niezbędne do tworzenia programów używających
biblioteki Z3.

%package -n python-z3
Summary:	Python 2 API for Z3 library
Summary(pl.UTF-8):	API języka Python 2 do biblioteki Z3
Group:		Libraries/Python
Requires:	%{name} = %{version}-%{release}

%description -n python-z3
Python 2 API for Z3 theorem prover library.

%description -n python-z3 -l pl.UTF-8
API języka Python 2 do biblioteki dowodzenia twierdzeń Z3.

%package -n python3-z3
Summary:	Python 3 API for Z3 library
Summary(pl.UTF-8):	API języka Python 3 do biblioteki Z3
Group:		Libraries/Python
Requires:	%{name} = %{version}-%{release}

%description -n python3-z3
Python 3 API for Z3 theorem prover library.

%description -n python3-z3 -l pl.UTF-8
API języka Python 3 do biblioteki dowodzenia twierdzeń Z3.

%prep
%setup -q -n z3-z3-%{version}
%patch -P0 -p1
%patch -P1 -p1

%if %{without sse2}
# no cmake option to disable, just architecture+compiler check
%{__sed} -i -e 's/if (HAS_SSE2)/if (FALSE)/' CMakeLists.txt
%endif

%build
%if %{with ocaml}
# ml not supported by CMakeLists.txt, need to generate some files
%if %{without ocaml_opt}
# hack to avoid configuration failure
OCAMLOPT=ocamlc \
%endif
%{__python3} scripts/mk_make.py \
	--ml
# --dotnet --java --python

# clean up so that cmake can be run
%{__rm} src/ast/pattern/database.h \
	src/util/z3_version.h \
	$(find src -name '*.hpp') \
	src/api/api_commands.cpp \
	src/api/api_log_macros.cpp \
	src/api/api_log_macros.h \
	src/api/dll/gparams_register_modules.cpp \
	src/api/dll/install_tactic.cpp \
	src/api/dll/mem_initializer.cpp \
	src/shell/gparams_register_modules.cpp \
	src/shell/install_tactic.cpp \
	src/shell/mem_initializer.cpp \
	src/test/gparams_register_modules.cpp \
	src/test/install_tactic.cpp \
	src/test/mem_initializer.cpp
%endif

# use (unofficial) cmake suite for regular build, because mk_make would
# require too much patching to comply with PLD standards (%{_lib}-awareness,
# optflags, verbose make...)

install -d build-cmake
cd build-cmake
%cmake .. \
	-DCMAKE_INSTALL_INCLUDEDIR=include/z3 \
	-DCMAKE_INSTALL_LIBDIR=%{_lib} \
	-DCMAKE_INSTALL_PYTHON_PKG_DIR=%{py3_sitescriptdir} \
	-DJAVA_HOME:PATH="%{java_home}" \
	-DPython3_EXECUTABLE:PATH="%{__python3}" \
	%{?with_apidocs:-DZ3_BUILD_DOCUMENTATION=ON} \
	%{?with_dotnet:-DZ3_BUILD_DOTNET_BINDINGS=ON} \
	-DZ3_BUILD_JAVA_BINDINGS=ON \
	-DZ3_BUILD_LIBZ3_SHARED=ON \
	-DZ3_BUILD_PYTHON_BINDINGS=ON \
	%{?with_dotnet:-DZ3_INSTALL_DOTNET_BINDINGS=ON} \
	-DZ3_INSTALL_JAVA_BINDINGS=ON \
	-DZ3_INSTALL_PYTHON_BINDINGS=ON \
	%{!?with_sse2:-DUSE_SSE2=OFF} \
	-DZ3_USE_LIB_GMP=ON

%{__make}

%if %{with ocaml}
# no cmake suite for ocaml; do it manually (basing on Makefile generated by mk_make.py from `configure --ml`)
install -d src/api/ml
cp -p ../build/api/ml/META src/api/ml
ocamlfind ocamlc -package zarith -ccopt "%{rpmcxxflags} -I../src/api -I../src/api/ml -o src/api/ml/z3native_stubs.o" -c ../src/api/ml/z3native_stubs.c
ocamlfind ocamlc -package zarith -i -I src/api/ml -c ../src/api/ml/z3enums.ml > src/api/ml/z3enums.mli
ocamlfind ocamlc -package zarith -I src/api/ml -o src/api/ml/z3enums.cmi -c src/api/ml/z3enums.mli
ocamlfind ocamlc -package zarith -I src/api/ml -o src/api/ml/z3enums.cmo -c ../src/api/ml/z3enums.ml
ocamlfind ocamlc -package zarith -i -I src/api/ml -o ../src/api/ml/z3native.ml > src/api/ml/z3native.mli
ocamlfind ocamlc -package zarith -I src/api/ml -o src/api/ml/z3native.cmi -c src/api/ml/z3native.mli
ocamlfind ocamlc -package zarith -I src/api/ml -o src/api/ml/z3native.cmo -c ../src/api/ml/z3native.ml
cp -p ../src/api/ml/z3.mli src/api/ml/z3.mli
ocamlfind ocamlc -package zarith -I src/api/ml -o src/api/ml/z3.cmi -c src/api/ml/z3.mli
ocamlfind ocamlc -package zarith -I src/api/ml -o src/api/ml/z3.cmo -c ../src/api/ml/z3.ml
ocamlmklib -o src/api/ml/z3ml -I src/api/ml src/api/ml/z3native_stubs.o src/api/ml/z3enums.cmo src/api/ml/z3native.cmo src/api/ml/z3.cmo -L. -lz3 -cclib -fopenmp
%if %{with ocaml_opt}
ocamlfind ocamlopt -package zarith -I src/api/ml -o src/api/ml/z3enums.cmx -c ../src/api/ml/z3enums.ml
ocamlfind ocamlopt -package zarith -I src/api/ml -o src/api/ml/z3native.cmx -c ../src/api/ml/z3native.ml
ocamlfind ocamlopt -package zarith -I src/api/ml -o src/api/ml/z3.cmx -c ../src/api/ml/z3.ml
ocamlmklib -o src/api/ml/z3ml -I src/api/ml src/api/ml/z3native_stubs.o src/api/ml/z3enums.cmx src/api/ml/z3native.cmx src/api/ml/z3.cmx -L. -lz3 -cclib -fopenmp
ocamlfind ocamlopt -package zarith -linkall -shared -o src/api/ml/z3ml.cmxs -I . -I src/api/ml src/api/ml/z3ml.cmxa
%endif
%endif

%install
rm -rf $RPM_BUILD_ROOT

%{__make} -C build-cmake install \
	DESTDIR=$RPM_BUILD_ROOT

%if %{with python2}
install -d $RPM_BUILD_ROOT%{py_sitescriptdir}
cp -pr $RPM_BUILD_ROOT%{py3_sitescriptdir}/z3 $RPM_BUILD_ROOT%{py_sitescriptdir}/z3

%py_comp $RPM_BUILD_ROOT%{py_sitescriptdir}
%py_ocomp $RPM_BUILD_ROOT%{py_sitescriptdir}
%py_postclean
%endif

%py3_comp $RPM_BUILD_ROOT%{py3_sitescriptdir}
%py3_ocomp $RPM_BUILD_ROOT%{py3_sitescriptdir}

%if %{with ocaml}
cd build-cmake
install -d $RPM_BUILD_ROOT%{_libdir}/ocaml/stublibs
ocamlfind install -destdir $RPM_BUILD_ROOT%{_libdir}/ocaml Z3 src/api/ml/META \
	src/api/ml/z3*.mli src/api/ml/z3*.cmi \
	src/api/ml/dllz3ml.so src/api/ml/libz3ml.a src/api/ml/z3ml.cma \
%if %{with ocaml_opt}
	src/api/ml/z3*.cmx \
	src/api/ml/z3ml.a src/api/ml/z3ml.cmxa src/api/ml/z3ml.cmxs
%endif

%{__rm} $RPM_BUILD_ROOT%{_libdir}/ocaml/stublibs/dllz3ml.so.owner
%if %{without ocaml_opt}
%{__sed} -i -e '/archive.*native/d' $RPM_BUILD_ROOT%{_libdir}/ocaml/Z3/META
%endif
cd ..
%endif

install -d $RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}
cp -a examples/* $RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}

# packaged as %doc in -apidocs
%{?with_apidocs:%{__rm} -r $RPM_BUILD_ROOT%{_docdir}/api}

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc LICENSE.txt README.md RELEASE_NOTES.md
%attr(755,root,root) %{_libdir}/libz3.so.*.*.*.*
%ghost %{_libdir}/libz3.so.4.15
%attr(755,root,root) %{_bindir}/z3

%files devel
%defattr(644,root,root,755)
%{_libdir}/libz3.so
%{_includedir}/z3
%{_pkgconfigdir}/z3.pc
%{_libdir}/cmake/z3
%{_examplesdir}/%{name}-%{version}

%if %{with apidocs}
%files apidocs
%defattr(644,root,root,755)
%doc build-cmake/doc/api/html/{search,*.{css,html,js,png}}
%endif

%files -n java-z3
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libz3java.so
%{_javadir}/com.microsoft.z3.jar

%if %{with ocaml}
%files -n ocaml-z3
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/ocaml/stublibs/dllz3ml.so
%dir %{_libdir}/ocaml/Z3
%{_libdir}/ocaml/Z3/META
%{_libdir}/ocaml/Z3/z3ml.cma
%if %{with ocaml_opt}
%attr(755,root,root) %{_libdir}/ocaml/Z3/z3ml.cmxs
%endif

%files -n ocaml-z3-devel
%defattr(644,root,root,755)
%{_libdir}/ocaml/Z3/libz3ml.a
%{_libdir}/ocaml/Z3/z3*.cmi
%{_libdir}/ocaml/Z3/z3*.mli
%if %{with ocaml_opt}
%{_libdir}/ocaml/Z3/z3ml.a
%{_libdir}/ocaml/Z3/z3*.cmx
%{_libdir}/ocaml/Z3/z3ml.cmxa
%endif
%endif

%if %{with python2}
%files -n python-z3
%defattr(644,root,root,755)
%{py_sitescriptdir}/z3
%endif

%files -n python3-z3
%defattr(644,root,root,755)
%{py3_sitescriptdir}/z3
