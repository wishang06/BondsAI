import markdown

def compile_AI_assessment(content):
    return markdown.markdown(content, extensions=['fenced_code', 'tables', 'extra'])