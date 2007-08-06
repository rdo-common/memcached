Name:           memcached
Version:        1.2.3
Release:        6%{?dist}
Summary:        High Performance, Distributed Memory Object Cache

Group:          System Environment/Daemons
License:        BSD
URL:            http://www.danga.com/memcached/
Source0:        http://www.danga.com/memcached/dist/%{name}-%{version}.tar.gz

# custom init script
Source1:        memcached.sysv

# Fixes
Patch1:		memcached-1.2.3-save_pid_fix.patch

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  libevent-devel
BuildRequires:  perl(Test::More)
Requires: initscripts
Requires(post): /sbin/chkconfig
Requires(preun): /sbin/chkconfig, /sbin/service
Requires(postun): /sbin/service

%description
memcached is a high-performance, distributed memory object caching
system, generic in nature, but intended for use in speeding up dynamic
web applications by alleviating database load.

%prep
%setup -q
%patch1 -p1



%build
%configure --enable-threads

make %{?_smp_mflags}


%check
# remove failing test that doesn't work in
# build systems
rm -f t/daemonize.t 
make test

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot} INSTALL="%{__install} -p"                                         
# remove memcached-debug
rm -f %{buildroot}/%{_bindir}/memcached-debug

# Perl script for monitoring memcached
install -Dp -m0755 scripts/memcached-tool %{buildroot}%{_bindir}/memcached-tool

# Init script
install -Dp -m0755 %{SOURCE1} %{buildroot}%{_initrddir}/memcached

# Default configs
mkdir -p %{buildroot}/%{_sysconfdir}/sysconfig
cat <<EOF >%{buildroot}/%{_sysconfdir}/sysconfig/%{name}
PORT="11211"
USER="nobody"
MAXCONN="1024"
CACHESIZE="64"
OPTIONS=""
EOF

# pid directory
mkdir -p %{buildroot}/%{_localstatedir}/run/memcached

%clean
rm -rf %{buildroot}


%post
/sbin/chkconfig --add %{name}

%preun
if [ "$1" = 0 ] ; then
    /sbin/service %{name} stop > /dev/null 2>&1
    /sbin/chkconfig --del %{name}
fi
exit 0

%postun
if [ "$1" -ge 1 ]; then
    /sbin/service %{name} condrestart > /dev/null 2>&1
fi
exit 0


%files
%defattr(-,root,root,-)
%doc AUTHORS ChangeLog COPYING NEWS README TODO doc/CONTRIBUTORS doc/*.txt
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}

%dir %attr(750,nobody,nobody) %{_localstatedir}/run/memcached
%{_bindir}/memcached-tool
%{_bindir}/memcached
%{_mandir}/man1/memcached.1*
%{_initrddir}/memcached


%changelog
* Mon Aug  6 2007 Paul Lindner <lindner@inuus.com> - 1.2.3-5
- Fix problem with -P and -d flag combo on x86_64
- Fix init script for FC-6

* Fri Jul 13 2007 Paul Lindner <lindner@inuus.com> - 1.2.3-4
- Remove test that fails in fedora build system on ppc64

* Sat Jul  7 2007 root <lindner@inuus.com> - 1.2.3-2
- Upgrade to 1.2.3 upstream
- Adjust make install to preserve man page timestamp
- Conform with LSB init scripts standards, add force-reload

* Wed Jul  4 2007 Paul Lindner <lindner@inuus.com> - 1.2.2-5
- Use /var/run/memcached/ directory to hold PID file

* Sat May 12 2007 Paul Lindner <lindner@inuus.com> - 1.2.2-4
- Remove tabs from spec file, rpmlint reports no more errors

* Thu May 10 2007 Paul Lindner <lindner@inuus.com> - 1.2.2-3
- Enable build-time regression tests
- add dependency on initscripts
- remove memcached-debug (not needed in dist)
- above suggestions from Bernard Johnson

* Mon May  7 2007 Paul Lindner <lindner@inuus.com> - 1.2.2-2
- Tidyness improvements suggested by Ruben Kerkhof in bugzilla #238994

* Fri May  4 2007 Paul Lindner <lindner@inuus.com> - 1.2.2-1
- Initial spec file created via rpmdev-newspec
