#%define init_daemon `cat /proc/1/comm`

Summary: Super important tool for nothing
Name: peter
Version: 1.0.0
Release: 1%{?dist}
License: Beerware
Source: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildArch: noarch

Requires: python-flask
Requires: python-jinja2

%description
Super important tool for nothing. They asked. I did.

%prep
%setup -q

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/%{_sbindir}
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/init.d
mkdir -p $RPM_BUILD_ROOT/%{_mandir}/man1/
mkdir -p $RPM_BUILD_ROOT/%{_prefix}/lib/systemd/system/
install -m 755 peter.py $RPM_BUILD_ROOT/%{_sbindir}/
install -m 644 peter.conf $RPM_BUILD_ROOT/%{_sysconfdir}/
install -m 644 peter.1.gz $RPM_BUILD_ROOT/%{_mandir}/man1/
install -m 755 peter.init $RPM_BUILD_ROOT/%{_sysconfdir}/init.d/peter
install -m 644 peter.service $RPM_BUILD_ROOT/%{_prefix}/lib/systemd/system/

%clean
rm -rf $RPM_BUILD_ROOT

%post
touch /var/log/peter.log
if [[ `cat /proc/1/comm` == "init" ]]; then
  /sbin/chkconfig --add peter >/dev/null 2>&1 || :;
  /sbin/chkconfig --level 345 peter on >/dev/null 2>&1 || :;
else
  /usr/bin/systemctl enable peter
fi

%preun
if [ $1 = 0 ]; then
  if [[ `cat /proc/1/comm` == "init" ]]; then
    /sbin/service peter stop >/dev/null 2>&1 || :;
    /sbin/chkconfig --del peter >/dev/null 2>&1 || :;
  else
    /usr/bin/systemctl stop peter
    /usr/bin/systemctl disable peter
  fi
fi

%postun
rm -f %{_prefix}/lib/systemd/system/peter.service
rm -f %{_sysconfdir}/init.d/peter
rm -f %{_sbindir}/peter.py >/dev/null 2>&1 || :;
rm -f %{_mandir}/man1/peter.1.*

%files
%defattr(-, root, root)
%doc README
%{_sysconfdir}/peter.conf
%{_sysconfdir}/init.d/peter
%{_sbindir}/peter.py
%{_mandir}/man1/peter.1.*
%{_prefix}/lib/systemd/system/peter.service

%changelog
* Sun Aug 21 2016 Stanislav Garifullin <corsair.home@gmail.com> - 1.0.0
- Napalm, son. Nothing else in the world smells like that. I love the smell of napalm in the morning. You know, one time we had a hill bombed, for 12 hours. When it was all over, I walked up. We didn’t find one of 'em, not one stinkin' dink body. The smell, you know that gasoline smell, the whole hill. Smelled like… victory. Someday this war’s gonna end.
