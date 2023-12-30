from django.utils.deprecation import MiddlewareMixin
import minify_html

class MinifyHTMLMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Check if 'Content-Type' header is in the response
        if 'Content-Type' in response and response['Content-Type'].split(';')[0] == 'text/html':
            response.content = minify_html.minify(response.content.decode('utf-8'), 
                                                  minify_js=True, 
                                                  minify_css=True, 
                                                  remove_processing_instructions=True).encode('utf-8')
        return response