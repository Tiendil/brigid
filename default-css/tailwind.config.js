/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ['../brigid/plugins/theme/templates/*.j2',
              '../brigid/plugins/theme/templates/**/*.j2'],
    theme: {
        extend: {
            typography: (theme) => ({
                DEFAULT: {
                    css: {
                        blockquote: {
                            quotes: 'none', // This disables the automatic quotes for <blockquotes>
                        }
                    },
                },
            }),
        },
    },
    plugins: [
        require('@tailwindcss/typography'),
    ],
}
