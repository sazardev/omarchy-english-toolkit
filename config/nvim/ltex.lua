local ltex_ls = vim.fn.expand("~/.local/opt/ltex/ltex-ls-plus-18.7.0/bin/ltex-ls-plus")

return {
  {
    "neovim/nvim-lspconfig",
    opts = {
      servers = {
        ltex_plus = {
          mason = false,
          cmd = { ltex_ls },
          filetypes = {
            "asciidoc",
            "bib",
            "gitcommit",
            "html",
            "mail",
            "markdown",
            "mdx",
            "org",
            "pandoc",
            "quarto",
            "rmd",
            "rst",
            "tex",
            "text",
            "typst",
            "xhtml",
          },
          settings = {
            ltex = {
              enabled = true,
              language = "en-GB",
              dictionary = "british",
              checkWhileTyping = true,
              diagnosticLevel = "hint",
              additionalRules = {
                EN_QUOTES = '"',
                EN_A_VS_AN = "a",
                EN_G_B = "-",
                COMMA_PARENTHESIS_WHITESPACE = true,
                SENTENCE_WHITESPACE = true,
                UPPERCASE_SENTENCE_START = true,
                WHITESPACE_RULE = true,
              },
              userSpecificRules = {
                "UPPERCASE_SENTENCE_START",
                "EN_NO_CONJUNCTIONS_START",
                "EN_NO_DOUBLE_PUNCTUATION",
              },
              userDictionary = table.concat({
                "collocations",
                "look forward to",
                "make a decision",
                "put up with",
                "regardless of",
                "in spite of",
                "on the other hand",
                "as far as I know",
                "would rather",
              }, ","),
            },
          },
        },
      },
    },
    keys = {
      { "<leader>ld", function() vim.diagnostic.open_float({ border = "rounded" }) end, desc = "Lsp float diagnostics" },
      { "<leader>le", function() vim.diagnostic.setloclist() end, desc = "Lsp diagnostics to loclist" },
      { "<leader>gl", function() vim.diagnostic.jump({ count = 0 }) end, desc = "Lsp next diagnostic" },
    },
  },
}
