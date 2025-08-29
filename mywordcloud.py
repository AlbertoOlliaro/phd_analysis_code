from matplotlib import pyplot as plt
from wordcloud import WordCloud


def create_wordcloud(text_dataframe, output_path, title):

    phrases = (
        text_dataframe.dropna().astype(str).str.split(';')
        .explode()
        .astype(str)
        .str.strip()
    )
    phrases = phrases[phrases.ne('')]
    freq = phrases.value_counts().to_dict()
    wordcloud = WordCloud(width=800, height=400, background_color='white',
                          collocations=False).generate_from_frequencies(freq)

    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(title)
    plt.savefig(output_path)
    plt.show()
    plt.close()

    return wordcloud
