from YoungLion import TextProcessor

text = "Contact team@example.com. Read https://example.com/docs for YoungLion documentation. YoungLion is fast."
tp = TextProcessor(text)
print(tp.stats())
print("Emails:", tp.extract_emails())
print("URLs:", tp.extract_urls())
print("Top words:", tp.most_frequent_words(5))
