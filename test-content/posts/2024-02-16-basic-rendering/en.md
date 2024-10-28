---
title = "Variants of basic rendering"
tags = ["example", "basic", "images"]
published_at = "2024-02-16T12:00:00+00:00"
seo_description = "Examples of rendering basic elements in web pages."
seo_image = ""
---

Here will be examples of basic elements rendering. Under the cut.

<!-- more -->

Header 1 is not allowed in the post body, it is reserved for the title.

## Header 2

### Header 3

#### Header 4

##### Header 5

###### Header 6

## Paragraphs and elements

This is a paragraph. It is separated from the next paragraph by an empty line.

This is a paragraph with a [link](https://example.com).

Here will be an ordered list:

1. First item
    1. First subitem
    2. Second subitem
2. Second item
3. Third item
    1. First subitem
    2. Second subitem


Here will be an unordered list:

- First item
    - First subitem
    - Second subitem
- Second item
- Third item
    - First subitem
    - Second subitem

Here will be a mixed list:

1. First item
    - First subitem
    - Second subitem
2. Second item
3. Third item
    - First subitem
    - Second subitem

One more mixed list:

- First item
    1. First subitem
    2. Second subitem
- Second item
- Third item
    1. First subitem
    2. Second subitem

Here will be a blockquote:

> This is a blockquote. It is separated from the next paragraph by an empty line.
>
> This is a blockquote with a [link](https://example.com).

Here will be a code block:

```
This is a code block.

x = y + 3

It is separated from the next paragraph by an empty line.
```

Here will be a horizontal rule:

---

## Basic elements

- **Bold text**
- *Italic text*
- ~~Strikethrough text~~
- `Inline code`

The same but in a quote:

> **Bold text**
>
> *Italic text*
>
> ~~Strikethrough text~~
>
> `Inline code`


## Links

[Link](https://example.com)

List with links:

- [Link 1](https://example.com)
- [Link 2](https://example.com)
- [Link 3](https://example.com)

raw link is a normal text: https://example.com

raw link in corner brackets is a link: <https://example.com>

**[strong link](https://example.com)**

_[italic link](https://example.com)_

## Markup in galery captions

/// brigid-images
src = "./images/image-1.jpg"
caption = """
Multiple paragraphs in the caption.

Basic elements:

- **Bold text**
- *Italic text*
- ~~Strikethrough text~~
- `Inline code`
- [Link](https://example.com)
"""
///

## Details / spoilers

/// details | Some summary
Some content
///

## Admonitions

/// admonition | Unstyled admonition
Some content
///

/// note | It is note

Some complex content

- 1
- 2
- **bold**

///

/// hint | It is hint
Some content
///

/// attention | It is attention
Luru ipsum dolor sit amet, consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
///

/// caution | It is caution
Some content
///

/// warning | It is warning
Some content
///

/// danger | It is danger
Some content
///

/// error | It is error
Some content
///
