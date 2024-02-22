---
title = "Example of snippets 2"
tags = ["example", "snippets"]
published_at = "2024-02-22T13:00:00+00:00"
description = "Examples of rendering snippets with relative imports."
seo_image = ""
---

Hi!

Here goes the first snippet with the same name as in the [Example of snippets 1]{post:test-snippets-1}.

--8<-- "./relative_snippet_1.md"

<!-- more -->

And here goes section snippet

```
--8<-- "./example.py:function_to_show"
```

And here should be dedented code snippet

```
--8<-- "./example.py:function_to_dedent"
```
