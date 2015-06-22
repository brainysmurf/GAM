GAMI: GAM Improved, GAM Importable GAM Installable-into-virtualenv
============================

In addition to GAM (below) this package adds the following features:

* Command line utility "gami" is installed into your path
* Installable into a virtualenv
* Import a helper function that can run exact same gam commands listed in wiki. No more piping out to the system
* Incorporates [click](http://click.pocoo.org/4/) and gets some bonus free-stuff, like automated help system, and python3 compatibility (although we have to change the print functions into click.echo calls, to start)

1) Install into a Virtualenv
-------------------------
Recommend using [pyenv](https://github.com/yyuu/pyenv) and [pyenv-virtualenv](https://github.com/yyuu/pyenv-virtualenv)
```
cd path_to_dir
pip install -e .
```
That's it. Now you have a new command line "gami"


2) Authenticate with Google
------------------------
From inside the directory, run python gam.py info domain and you'll get the usual rigamorle. You have to do this first before being able to use gami or the helper function


3a) Use "gami" command line utility
----------
```
gami --help
```
All the functions have help too.


3b) Import a helper function
----------------------------
```
from gami import run_gami_from_string
run_gami_from_string('gam info domain')    # any regular gam command
```

That function returns a python dictionary


What's different from Ditto Gam?
--------------------------------
It provides a more modern cli interface, but manages to sort of "bootstrap" the old code, so nothing is broken, you can still use the same old commands in the same old way, but you can also opt-in on these other features.


How does it work?
-----------------
Most of the magic happens in cli/cli.py, and most of the heavy lifing is done with click. 



Dito GAM
============================
GAM is a free, open source command line tool for
Google Apps Administrators to efficiently manage
domain and user settings quickly and easily. GAM has support
for many features, such as

* creating, deleting, and updating users, aliases, groups, 
  organizations, and resource calendars
* modifying user email settings such as IMAP, signatures,
  vacation messages, profile sharing, email forwarding,
  send as address, labels, and features.
* delegating mailboxes and calendars to other users
* modifying calendar access rights for users and resource calendars.
* auditing user accounts and mailboes
* monitoring incoming and outgoing email
* generating detailed reports for users, groups, resources,
  account activity, email clients, and quotas.

Downloads
---------
You can download current GAM from 
the [GitHub Releases] page.

Documentation
------------------
The GAM documentation is currently hosted in the [GitHub Wiki]

Mailing List / Discussion group
-------------------------------
The GAM mailing list / discussion group is hosted
on [Google Groups].  You can join the list and interact
via email, or just post from the web itself.

Source Repository
-----------------

The official GAM source repository is on [GitHub].

Author
------

GAM is maintained by <a href="mailto:jay0lee@gmail.com">Jay Lee</a>.

Thanks To
---------

GAM is made possible and maintained by the work of Dito.
Who is Dito?

*Dito is solely focused on moving organizations to Google's
cloud. After hundreds of successful deployments over the
last 5 years, we have gained notoriety for our complete
understanding of the platform, our change management &
training ability, and our rock-star deployment engineers.
We are known worldwide as the Google Apps Experts.*

Need a Google Apps Expert? 
[Contact Dito](http://ditoweb.com/contact), which offers
[free premium GAM support](http://www.ditoweb.com/dito-gam)
for domains that sign up through Dito.

[GitHub Releases]: https://github.com/jay0lee/GAM/releases
[GitHub]: https://github.com/jay0lee/GAM/
[GitHub Wiki]: https://github.com/jay0lee/GAM/wiki/
[Google Groups]: http://groups.google.com/group/google-apps-manager
