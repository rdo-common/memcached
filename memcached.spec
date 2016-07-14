%define username   memcached
%define groupname  memcached
%bcond_without sasl

Name:           memcached
Version:        1.4.29
Release:        1%{?dist}
Epoch:          0
Summary:        High Performance, Distributed Memory Object Cache

Group:          System Environment/Daemons
License:        BSD
URL:            http://www.memcached.org/
Source0:        http://www.memcached.org/files/%{name}-%{version}.tar.gz
Source1:        memcached.sysconfig

Patch1:         memcached-unit.patch

BuildRequires:  libevent-devel systemd-units
BuildRequires:  perl-generators
BuildRequires:  perl(Test::More), perl(Test::Harness)
%{?with_sasl:BuildRequires: cyrus-sasl-devel}

Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
Requires(pre):  shadow-utils

%description
memcached is a high-performance, distributed memory object caching
system, generic in nature, but intended for use in speeding up dynamic
web applications by alleviating database load.

%package devel
Summary: Files needed for development using memcached protocol
Group: Development/Libraries
Requires: %{name} = %{epoch}:%{version}-%{release}

%description devel
Install memcached-devel if you are developing C/C++ applications that require
access to the memcached binary include files.

%prep
%setup -q
%patch1 -p1 -b .unit

%build
# compile with full RELRO
export CFLAGS="%{optflags} -pie -fpie"
export LDFLAGS="-Wl,-z,relro,-z,now"

%configure \
  %{?with_sasl: --enable-sasl}

make %{?_smp_mflags}

%check
# whitespace tests fail locally on fedpkg systems now that they use git
rm -f t/whitespace.t

# Parts of the test suite only succeed as non-root.
if [ `id -u` -ne 0 ]; then
  # remove failing test that doesn't work in
  # build systems
  rm -f t/daemonize.t t/watcher.t t/expirations.t
fi
make test

%install
make install DESTDIR=%{buildroot} INSTALL="%{__install} -p"
# remove memcached-debug
rm -f %{buildroot}/%{_bindir}/memcached-debug

# Perl script for monitoring memcached
install -Dp -m0755 scripts/memcached-tool %{buildroot}%{_bindir}/memcached-tool
install -Dp -m0644 scripts/memcached-tool.1 \
        %{buildroot}%{_mandir}/man1/memcached-tool.1

# Unit file
install -Dp -m0644 scripts/memcached.service \
        %{buildroot}%{_unitdir}/memcached.service

# Default configs
install -Dp -m0644 %{SOURCE1} %{buildroot}/%{_sysconfdir}/sysconfig/%{name}


%pre
getent group %{groupname} >/dev/null || groupadd -r %{groupname}
getent passwd %{username} >/dev/null || \
useradd -r -g %{groupname} -d /run/memcached \
    -s /sbin/nologin -c "Memcached daemon" %{username}
exit 0


%post
%systemd_post memcached.service


%preun
%systemd_preun memcached.service


%postun
%systemd_postun_with_restart memcached.service


%files
%doc AUTHORS ChangeLog COPYING NEWS README.md doc/CONTRIBUTORS doc/*.txt
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%{_bindir}/memcached-tool
%{_bindir}/memcached
%{_mandir}/man1/memcached-tool.1*
%{_mandir}/man1/memcached.1*
%{_unitdir}/memcached.service


%files devel
%{_includedir}/memcached/*

%changelog
* Thu Jul 14 2016 Miroslav Lichvar <mlichvar@redhat.com> - 0:1.4.29-1
- update to 1.4.29

* Tue Jul 12 2016 Miroslav Lichvar <mlichvar@redhat.com> - 0:1.4.28-1
- update to 1.4.28
- listen only on loopback interface by default (#1182542)
- use upstream unit file (#1350939)
- remove obsolete macros and scriptlet

* Tue Jun 21 2016 Miroslav Lichvar <mlichvar@redhat.com> - 0:1.4.26-1
- update to 1.4.26

* Tue Feb 23 2016 Miroslav Lichvar <mlichvar@redhat.com> - 0:1.4.25-1
- update to 1.4.25
- enable SASL support (#815050)
- remove obsolete macros

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0:1.4.17-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.4.17-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.4.17-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.4.17-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed Jan 15 2014 Miroslav Lichvar <mlichvar@redhat.com> - 0:1.4.17-1
- update to 1.4.17
- fix building with -Werror=format-security in CFLAGS

* Wed Aug 07 2013 Miroslav Lichvar <mlichvar@redhat.com> - 0:1.4.15-7
- buildrequire systemd-units (#992221)
- update memcached man page
- add memcached-tool man page

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.4.15-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Jul 17 2013 Petr Pisar <ppisar@redhat.com> - 0:1.4.15-5
- Perl 5.18 rebuild

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.4.15-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Thu Dec 20 2012 Miroslav Lichvar <mlichvar@redhat.com> - 0:1.4.15-3
- compile with full RELRO

* Tue Nov 20 2012 Joe Orton <jorton@redhat.com> - 0:1.4.15-2
- BR perl(Test::Harness)

* Tue Nov 20 2012 Joe Orton <jorton@redhat.com> - 0:1.4.15-1
- update to 1.4.15 (#782395)
- switch to simple systemd service (#878198)
- use systemd scriptlet macros (Václav Pavlín, #850204)

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.4.13-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri May 04 2012 Jon Ciesla <limburgher@gmail.com> - 0:1.4.13-2
- Migrate to systemd, 783112.

* Tue Feb  7 2012 Paul Lindner <lindner@mirth.inuus.com> - 0:1.4.13-1
- Upgrade to memcached 1.4.13
- http://code.google.com/p/memcached/wiki/ReleaseNotes1413
- http://code.google.com/p/memcached/wiki/ReleaseNotes1412
- http://code.google.com/p/memcached/wiki/ReleaseNotes1411

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.4.10-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Nov  9 2011 Paul Lindner <lindner@mirth.inuus.com> - 0:1.4.10-1
- Upgrade to memcached 1.4.10 (http://code.google.com/p/memcached/wiki/ReleaseNotes1410)

* Tue Aug 16 2011 Paul Lindner <lindner@inuus.com> - 0:1.4.7-1
- Upgrade to memcached 1.4.7 (http://code.google.com/p/memcached/wiki/ReleaseNotes147)
- Fix some rpmlint errors/warnings.

* Tue Aug  2 2011 Paul Lindner <lindner@inuus.com> - 0:1.4.6-1
- Upgrade to memcached-1.4.6

* Wed Feb 16 2011 Joe Orton <jorton@redhat.com> - 0:1.4.5-7
- fix build

* Mon Feb 14 2011 Paul Lindner <lindner@inuus.com> - 0:1.4.5-6
- Rebuild for updated libevent

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.4.5-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sun Nov 28 2010 Paul Lindner <lindner@inuus.com> - 0:1.4.5-4
- Add code to deal with /var/run/memcached on tmpfs

* Wed Sep  8 2010 Paul Lindner <lindner@inuus.com> - 0:1.4.5-3
- Apply patch from memcached issue #60, solves Bugzilla 631051

* Wed May 26 2010 Joe Orton <jorton@redhat.com> - 0:1.4.5-2
- LSB compliance fixes for init script
- don't run the test suite as root
- ensure a constant timestamp on the sysconfig file

* Sun Apr  4 2010 Paul Lindner <lindner@inuus.com> - 0:1.4.5-1
- Upgrade to upstream memcached-1.4.5 (http://code.google.com/p/memcached/wiki/ReleaseNotes145)

* Wed Jan 20 2010 Paul Lindner <lindner@inuus.com> - 0:1.4.4-2
- Remove SELinux policies fixes Bugzilla 557073

* Sat Nov 28 2009 Paul Lindner <lindner@inuus.com> - 0:1.4.4-1
- Upgraded to upstream memcached-1.4.4 (http://code.google.com/p/memcached/wiki/ReleaseNotes144)
- Add explicit Epoch to fix issue with broken devel dependencies (resolves 542001)

* Thu Nov 12 2009 Paul Lindner <lindner@inuus.com> - 1.4.3-1
- Add explicit require on memcached for memcached-devel (resolves 537046)
- enable-threads option no longer needed
- Update web site address

* Wed Nov 11 2009 Paul Lindner <lindner@inuus.com> - 1.4.3-1
- Upgrade to memcached-1.4.3

* Mon Oct 12 2009 Paul Lindner <lindner@inuus.com> - 1.4.2-1
- Upgrade to memcached-1.4.2
- Addresses CVE-2009-2415

* Sat Aug 29 2009 Paul Lindner <lindner@inuus.com> - 1.4.1-1
- Upgrade to 1.4.1
- http://code.google.com/p/memcached/wiki/ReleaseNotes141

* Wed Apr 29 2009 Paul Lindner <lindner@inuus.com> - 1.2.8-1
- Upgrade to memcached-1.2.8
- Addresses CVE-2009-1255

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Tue Jul 29 2008 Paul Lindner <lindner@inuus.com> - 1.2.6-1
- Upgrade to memcached-1.2.6

* Tue Mar  4 2008 Paul Lindner <lindner@inuus.com> - 1.2.5-1
- Upgrade to memcached-1.2.5

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 1.2.4-4
- Autorebuild for GCC 4.3

* Sun Jan 27 2008 Paul Lindner <lindner@inuus.com> - 1.2.4-3
- Adjust libevent dependencies

* Sat Dec 22 2007 Paul Lindner <lindner@inuus.com> - 1.2.4-2
- Upgrade to memcached-1.2.4

* Fri Sep 07 2007 Konstantin Ryabitsev <icon@fedoraproject.org> - 1.2.3-8
- Add selinux policies
- Create our own system user

* Mon Aug  6 2007 Paul Lindner <lindner@inuus.com> - 1.2.3-7
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
