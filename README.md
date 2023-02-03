# Description

This is a simple web site for scheduling appointments for mikvah.

It's meant to be very easy to use and privacy sensitive.

It encourages scheduling appointments close together, but not too many to handle.

It prevents scheduling appointments before the zman.

Shabbes works slightly differently, first come first served starting at the zman.

You'll need to change the source for your own: time zone, geographic location, and appointment rate.

# HOWTO sketch

All you need is support for python, django, and postgres (or similar).

To set it up, you're going to want to be familiar with django, or go through the tutorial. Start a project and wire in this code as an app. Migrate its database schema, and ideally make its background image availabe as a static web page. (This may be as easy as copying from the mikvah/static directory to your site's static directory.)

Consider using https://fly.io to serve up the site for free, since it should be pretty light. Keep portability by [registering](https://domains.google/) and serving your own domain name.

Besides the django admin, there are really only two entry points:

/mikvah - for scheduling appointments

/mikvah/attendant - for vieweing appointments

You're going to want to password protect the latter.
