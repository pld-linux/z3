Summary:	high-performance theorem prover developed at Microsoft Research
Name:		z3
Version:	4.3.1
Release:	0.1
License:	MSR-LA Non-Commercial Use Only
Group:		Applications/Engineering
# git clone https://git01.codeplex.com/z3
# git co v%{version}
Source0:	%{name}-%{version}.tar.gz
# Source0-md5:	59651c37211dd86f50dc7d90e897157d
URL:		http://z3.codeplex.com/
BuildRequires:	python
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Z3 is a high-performance theorem prover being developed at Microsoft
Research.

%package devel
Summary:	Development files for Z3
Group:		Development/Libraries

%description devel
Development files for Z3.

%prep
%setup -q

%build
%{__autoconf}
%configure \
	CXX="g++"

python scripts/mk_make.py
cd build
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{_includedir}/%{name},%{_libdir}} \
	$RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}

cp src/api/z3{,_api,_v1,_macros}.h $RPM_BUILD_ROOT%{_includedir}/%{name}
cp src/api/c++/z3++.h $RPM_BUILD_ROOT%{_includedir}/%{name}
install build/z3 $RPM_BUILD_ROOT%{_bindir}
install build/libz3.so $RPM_BUILD_ROOT%{_libdir}

cp -a examples/* $RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc LICENSE.txt README RELEASE_NOTES
%attr(755,root,root) %{_bindir}/%{name}*

%files devel
%defattr(644,root,root,755)
%{_includedir}/%{name}
%attr(755,root,root) %{_libdir}/libz3.so
%{_examplesdir}/%{name}-%{version}
