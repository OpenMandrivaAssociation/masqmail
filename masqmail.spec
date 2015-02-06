%define confdir		%{_sysconfdir}/masqmail
%define spooldir	%{_var}/spool/masqmail
%define logdir		%{_var}/log/masqmail
%define mailuser	mail
%define mailgroup	mail

# include AUTH (RFC 2554) client support:
%define with_AUTH_CL	1
# include ident (RFC 1413) client support:
%define with_IDENT_CL	0
# include qmail-style maildir support:
%define with_MAILDIR	0
# include MasqDial support:
%define with_MSERVER	0
# include fetchmail-like POP3 client support:
%define with_POP3_CL	0
# link with libcrypto:
%define with_LIBCRYPTO	1

Summary:	Offline Mail Transfert Agent
Name:		masqmail
Version:	0.2.18
Release:	18
Epoch:		1
License:	GPLv2+
Group:		System/Servers
Url:		http://masqmail.cx/masqmail/
Source0:	%{name}-%{version}.tar.bz2
Source3:	%{name}.service
Source4:	masqmail-etc-masqmail-masqmail.conf
Source5:	masqmail-etc-masqmail-example.route
Patch0:		masqmail-Makefile_no_chown.patch.bz2
BuildRequires:	pkgconfig(glib)
%if %{with_LIBCRYPTO}
BuildRequires:	pkgconfig(openssl)
%endif
Requires(preun,post):	rpm-helper
Requires(post): 	systemd-units
Requires(preun): 	systemd-units
Requires(postun): 	systemd-units
Provides:	sendmail-command
Provides:	mail-server

%description
MasqMail is a mail server designed for hosts that are not permanently
connected to the Internet. It handles outgoing messages specially and
delivers them only when the Internet connection is available.
It has support for multiple Internet Service Providers and for local
users's mail boxes. It replaces other MTAs such as Sendmail or Postfix.

%files
%doc AUTHORS ChangeLog COPYING INSTALL NEWS README TODO
%dir %{_datadir}/masqmail
%dir %{_datadir}/masqmail/tpl
%dir %{_datadir}/masqmail/tpl/*
%{_mandir}/man5/masqmail.aliases.5*
%{_mandir}/man5/masqmail.conf.5*
%if %{with_POP3_CL}
%{_mandir}/man5/masqmail.get.5*
%endif
%{_mandir}/man5/masqmail.route.5*
%{_mandir}/man8/masqmail.8*
%if %{with_MSERVER}
%{_mandir}/man8/mservdetect.8*
%{_bindir}/mservdetect
%endif
%attr(04711, root, root) %{_sbindir}/masqmail

%dir %{confdir}
%config(noreplace) %{confdir}/masqmail.conf
%if %{with_POP3_CL}
%config(noreplace) %{confdir}/example.get
%endif
%config(noreplace) %{confdir}/example.route
%{_unitdir}/%{name}.service

%defattr(-, %{mailuser}, %{mailgroup}, 0755)
%dir %{logdir}
%dir %{spooldir}
%dir %{spooldir}/input
%dir %{spooldir}/lock
%dir %{spooldir}/popuidl

%post
# Install alternatives:
update-alternatives --install %{_sbindir}/sendmail sendmail-command %{_sbindir}/masqmail 20 \
        --slave %{_libdir}/sendmail sendmail-command-in_libdir %{_sbindir}/masqmail \
        --slave %{_mandir}/man1/sendmail.1.bz2 sendmail-command-man %{_mandir}/man8/masqmail.8*

%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

if [ $1 = 0 ]; then
# Clean up spool:
	for dir in input lock popuidl; do
		test -d %{spooldir}/$dir && /bin/rm -f %{spooldir}/$dir/*
	done
# Clean up logs:
	/bin/rm -f %{logdir}/*
# Remove alternatives:
        update-alternatives --remove sendmail-command %{_sbindir}/masqmail
fi

%postun
%systemd_postun_with_restart %{name}.service

#----------------------------------------------------------------------------

%prep
%setup -q
%patch0 -p1

%build
CFGFLAGS=""
%if %{with_AUTH_CL}
CFGFLAGS="$CFGFLAGS --enable-auth"
%endif
%if %{with_IDENT_CL}
CFGFLAGS="$CFGFLAGS --enable-ident"
%endif
%if %{with_MAILDIR}
CFGFLAGS="$CFGFLAGS --enable-maildir"
%endif
%if %{with_MSERVER}
CFGFLAGS="$CFGFLAGS --enable-mserver"
%endif
CFGFLAGS="$CFGFLAGS --disable-pop3"
%if %{with_POP3_CL}
CFGFLAGS=OLDCFGFLAGS
%endif
%if %{with_LIBCRYPTO}
CFGFLAGS="$CFGFLAGS --with-libcrypto"
%endif

%serverbuild

%configure2_5x \
	--with-user=%{mailuser} \
	--with-group=%{mailgroup} \
	--with-conf-dir=%{confdir} \
	--with-logdir=%{logdir} \
	--with-spooldir=%{spooldir} \
	--disable-debug $CFGFLAGS \
%ifarch x86_64
	--disable-resolver
%endif

%make

%install
%makeinstall_std

# systemd service:
install -D -m 644 %{SOURCE3} %{buildroot}%{_unitdir}/%{name}.service

# Configuration files:
cp %{SOURCE4} %{buildroot}%{confdir}/masqmail.conf
cp %{SOURCE5} %{buildroot}%{confdir}/example.route
%if %{with_POP3_CL}
	cp examples/example.get %{buildroot}%{confdir}/example.get
%endif

# Unused files:
%if !%{with_POP3_CL}
	rm %{buildroot}%{_mandir}/man5/masqmail.get.5*
%endif

%if !%{with_MSERVER}
	rm %{buildroot}%{_mandir}/man8/mservdetect.8*
	rm %{buildroot}%{_bindir}/mservdetect
%endif
