import re
from tidylib import tidy_document, tidy_fragment

from django.conf import settings
from django.http import HttpResponse, HttpResponseServerError
from django.template import Context, Template


class HTMLValidationMiddleware(object):
    ignore = [
        'trimming empty <option>',
        '<table> lacks "summary" attribute',
    ]

    # Options for tidy. Can be overridden with HTML_VALIDATION_OPTIONS setting
    options = {
        # 'doctype': getattr(settings, 'HTML_VALIDATION_DOCTYPE', 'strict'),
        # 'output_xhtml': getattr(settings, 'HTML_VALIDATION_XHTML', True),
        # 'input_encoding': getattr(settings, 'HTML_VALIDATION_ENCODING', 'utf8'),
    }

    def __init__(self):
        if not settings.DEBUG or not getattr(settings, 'HTML_VALIDATION_ENABLE', True):
            raise MiddlewareNotUsed

        self.options = getattr(settings, 'HTML_VALIDATION_OPTIONS', self.options)
        self.ignore = set(getattr(settings, 'HTML_VALIDATION_IGNORE', self.ignore))
        self.ignore_regexp = self._build_ignore_regexp(getattr(settings, 'HTML_VALIDATION_URL_IGNORE', []))
        self.template = Template(self.HTML_VALIDATION_TEMPLATE.strip())

    def process_response(self, request, response):
        # if not self._should_validate(request, response):
        #     return response
        return response

        errors = self._validate(response)

        if not errors:
            return response

        context = self._get_context(response, errors)

        return HttpResponseServerError(self.template.render(context))

    def _build_ignore_regexp(self, urls):
        if not urls:
            return None

        urls = [r'(%s)' % url for url in urls]
        return re.compile(r'(%s)' % r'|'.join(urls))

    def _should_validate(self, request, response):
        return ('html' in response['Content-Type'] and
                'disable-validation' not in request.GET and
                not request.is_ajax() and
                (not self.ignore_regexp or
                 not self.ignore_regexp.search(request.path)) and
                request.META['REMOTE_ADDR'] in settings.INTERNAL_IPS and
                type(response) == HttpResponse)

    def _validate(self, response):
        document, errors = tidy_document(response.content, **self.options)
        return errors

    def _filter_errors(self, errors):
        return filter(lambda e: e.message not in self.ignore, errors)

    def _get_context(self, response, errors):
        lines = []
        # error_dict = dict(map(lambda e: e, errors))

        # for i, line in enumerate(response.content.split('\n')):
        #     lines.append((line, error_dict.get(i + 1, False)))

        return Context({'errors': errors.split('\n'),
                        'lines': lines,})

    HTML_VALIDATION_TEMPLATE = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html lang="en">
<head>
  <meta http-equiv="content-type" content="text/html; charset=utf-8">
  <title>HTML validation error at {{ request.path_info|escape }}</title>
  <meta name="robots" content="NONE,NOARCHIVE">
  <style type="text/css">
    html * { padding: 0; margin: 0; }
    body * { padding: 10px 20px; }
    body * * { padding: 0; }
    body { font: small sans-serif; background: #eee; }
    body>div { border-bottom: 1px solid #ddd; }
    h1 { font-weight: normal; margin-bottom: 0.4em; }
    table { border: none; border-collapse: collapse; width: 100%; }
    td, th { vertical-align: top; padding: 2px 3px; }
    th { width: 6em; text-align: right; color: #666; padding-right: 0.5em; }
    #info { background: #f6f6f6; }
    #info th { width: 3em; }
    #summary { background: #ffc; }
    #explanation { background: #eee; border-bottom: 0px none; }
    .meta { margin: 1em 0; }
    .error { background: #FEE }
  </style>
</head>
<body>
  <div id="summary">
    <h1>HTML validation error</h1>
    <p>
        Your HTML did not validate. If this page contains user content that
        might be the problem. Please fix the following:
    </p>
    <table class="meta">
      {% for error in errors %}
        <tr>
          <th>Line: <a href="#line{{ error.line }}">{{ error.line }}</a></th>
          <td>{{error}}</td>
        </tr>
      {% endfor %}
    </table>
    <p>
      If you want to bypass this warning, click <a href="?disable-validation">
      here</a>. Please note that this warning will persist until you fix the
      problems mentioned above.
    </p>
  </div>
  <div id="info">
    <table>
      {% for line,error in lines %}
        <tr{% if error %} class="error"{% endif %}>
          <th id="line{{ forloop.counter }}">
            {{ forloop.counter|stringformat:"03d" }}
          </th>
          <td{% if error %} title="{{ error }}"{% endif %}>
            <pre>{{ line }}</pre>
          </td>
        </tr>
      {% endfor %}
    </table>
  </div>

  <div id="explanation">
    <p>
      You're seeing this error because you have not set
      <code>HTML_VALIDATION_ENABLE = False</code> in your Django settings file.
      Change that to <code>False</code>, and Django will stop validating your
      HTML.
    </p>
  </div>
</body>
</html>"""
