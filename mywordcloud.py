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

    # Dynamic sizing based on number of unique words
    n_words = max(1, len(freq))
    aspect_ratio = 2.0  # width:height
    # Base size grows with sqrt of number of words, capped to avoid extremes
    base_height = max(300, min(1000, int(45 * (n_words ** 0.5))))
    width = int(base_height * aspect_ratio)
    height = base_height

    # Higher scale => higher pixel density in the rendered word cloud
    render_scale = 2

    wordcloud = WordCloud(
        width=width,
        height=height,
        scale=render_scale,
        background_color='white',
        collocations=False,
        max_words=n_words,  # ensure we consider all words in freq
        min_font_size=8
    ).generate_from_frequencies(freq)

    plt.figure(figsize=(width / 100, height / 100))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(title)
    plt.savefig(output_path, dpi=100)  # dpi aligns with figsize; scale controls pixel density
    plt.show()
    plt.close()

    return wordcloud

