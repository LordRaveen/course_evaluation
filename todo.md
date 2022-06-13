# How to add a page

Lets say a page `about` is to be created

1.  create a file `about.html` in templates folder
2.  the contents of `about.html`

    1| {% extends "layout.html" %}
    2| {% block title %} Users {% endblock %}}
    3|
    4| {% block body %}
    5| <!-- main content[html]  goes here -->
    6| <div>
    7|  <h2>About Us</h2>
    8|  <p>This is who we are</p>
    9| </div>
    10| {% endblock %}

3.  Then go to `views.py` and do the following:

    1| @views.route('/about')
    2| @is_logged_in <!-- used for pages that require login. eg profile page -->
    3| def about():
    4| return render_template('about.html')
    5|
