# masqmail.spec.  Generated from masqmail.spec.in by configure.
# Mandrake GNU/Linux RPM specfile for MasqMail
# $Id$
#
# Process this file with ./config.status --file=mandrake/masqmail.spec
# once you have properly configured the source package.

%define name		masqmail
%define version		0.2.18

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


Name:		%{name}
Summary:	Offline Mail Transfert Agent
Version:	%{version}
Release:	%mkrel 13
Epoch:		1
URL:		http://masqmail.cx/masqmail/
Source0:	masqmail-%{version}.tar.bz2
Source3:	masqmail-etc-init.d-masqmail
Source4:	masqmail-etc-masqmail-masqmail.conf
Source5:	masqmail-etc-masqmail-example.route
Patch0:		masqmail-Makefile_no_chown.patch.bz2

License:	GPL
Group:		System/Servers
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot

Provides:	sendmail-command, mail-server
Requires(preun):		rpm-helper
Requires(post):		rpm-helper

BuildRequires:	glib-devel >= 1.0

%if %{with_LIBCRYPTO}
BuildRequires:	libopenssl-devel
%endif


%description
MasqMail is a mail server designed for hosts that are not permanently
connected to the Internet. It handles outgoing messages specially and
delivers them only when the Internet connection is available.
It has support for multiple Internet Service Providers and for local
users's mail boxes. It replaces other MTAs such as Sendmail or Postfix.


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

%configure --with-user=%{mailuser} --with-group=%{mailgroup} \
        --with-conf-dir=%{confdir} --with-logdir=%{logdir} \
        --with-spooldir=%{spooldir} --disable-debug $CFGFLAGS \
%ifarch x86_64
     --disable-resolver
%endif


%make


%install
/bin/rm -Rf %buildroot
make DESTDIR=%buildroot install-strip

# Init script:
/bin/mkdir -p %buildroot/%{_sysconfdir}/rc.d/init.d/
install -m 0744 %{SOURCE3} %buildroot/%{_sysconfdir}/rc.d/init.d/masqmail

# Configuration files:
/bin/cp %{SOURCE4} %buildroot/%{confdir}/masqmail.conf
/bin/cp %{SOURCE5} %buildroot/%{confdir}/example.route
%if %{with_POP3_CL}
/bin/cp examples/example.get %buildroot/%{confdir}/example.get
%endif

# Unused files:
%if ! %{with_POP3_CL}
/bin/rm %buildroot/%{_mandir}/man5/masqmail.get.5*
%endif

%if ! %{with_MSERVER}
/bin/rm %buildroot/%{_mandir}/man8/mservdetect.8*
/bin/rm %buildroot/%{_bindir}/mservdetect
%endif

%clean
/bin/rm -Rf %buildroot


%files
%defattr(-, root, root, 0755)
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
%attr(0744, root, root) %config(noreplace) %{_sysconfdir}/rc.d/init.d/masqmail

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
# Install service:
%_post_service masqmail


%preun
# Remove service:
%_preun_service masqmail

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


%changelog
* Mon Dec 06 2010 Oden Eriksson <oeriksson@mandriva.com> 1:0.2.18-13mdv2011.0
+ Revision: 612837
- the mass rebuild of 2010.1 packages

* Mon Apr 19 2010 Funda Wang <fwang@mandriva.org> 1:0.2.18-12mdv2010.1
+ Revision: 536604
- rebuild

* Fri Sep 04 2009 Thierry Vignaud <tv@mandriva.org> 1:0.2.18-11mdv2010.0
+ Revision: 429956
- rebuild

* Mon Jul 28 2008 Thierry Vignaud <tv@mandriva.org> 1:0.2.18-10mdv2009.0
+ Revision: 251892
- rebuild
- fix no-buildroot-tag

* Mon Dec 17 2007 Thierry Vignaud <tv@mandriva.org> 1:0.2.18-8mdv2008.1
+ Revision: 129743
- kill re-definition of %%buildroot on Pixel's request
- do not hardcode man pages extension

  + Michael Scherer <misc@mandriva.org>
    - Import masqmail





* Mon May 01 2006 Michael Scherer <misc@mandriva.org> 1:0.2.18-8mdk
- fix x86_64 build
- clean rpmlint error

* Sun Mar 19 2006 Michael Scherer <misc@mandriva.org> 1:0.2.18-7mdk
- Rebuild for new openssl
- use -q for setup
- clean buildroot at install time
- fix rpmbuildupdatability

* Thu Jul 21 2005 Gaetan Lehmann <gaetan.lehmann@jouy.inra.fr> 0.2.18-6mdk
- complete sendmail-command alternative

* Thu Jul 21 2005 Gaetan Lehmann <gaetan.lehmann@jouy.inra.fr> 0.2.18-5mdk
- fix alternative (Michael Reinsch)

* Fri Jul  1 2005 Gaetan Lehmann <gaetan.lehmann@jouy.inra.fr> 0.2.18-4mdk
- provides and alternative sendmail-command
- use mkrel

* Tue Feb 10 2004 Lenny Cartier <lenny@mandrakesoft.com> 0.2.18-3mdk
- disable-resolver on amd64
- close endif

* Mon Sep 22 2003 Lenny Cartier <lenny@mandrakesoft.com> 0.2.18-2mdk
- fix requires

* Tue Dec 31 2002 Lenny Cartier <lenny@mandrakesoft.com> 0.2.18-1mdk
- from Rémi Denis-Courmont <rdenis@simphalempin.com> :
	- Resync with mainstream version
	- Error templates moved to /usr/share
	- Fixed mservdetect manpage path
	- Optionnaly unused files removed from build root

* Sun Nov 17 2002 Rémi Denis-Courmont <rdenis@simphalempin.com> 0.2.16-1mdk
- Resync with mainstream version
- MTA alternatives no longer removed when upgrading package

* Sat Nov 09 2002 Rémi Denis-Courmont <rdenis@simphalempin.com> 0.2.15-1mdk
- Resync with mainstream version

* Sat Nov 02 2002 Rémi Denis-Courmont <rdenis@simphalempin.com> 0.2.14-1mdk
- Specfile created for Mandrake
- Init script created
- New masqmail.conf and example.route created
