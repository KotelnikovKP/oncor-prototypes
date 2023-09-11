export default {
    // Target: https://go.nuxtjs.dev/config-target
    target: 'static',

    // Global page headers: https://go.nuxtjs.dev/config-head
    head: {
        title: 'frontend',
        htmlAttrs: {
            lang: 'en'
        },
        meta: [
            { charset: 'utf-8' },
            { name: 'viewport', content: 'width=device-width, initial-scale=1' },
            { hid: 'description', name: 'description', content: '' },
            { name: 'format-detection', content: 'telephone=no' }
        ],
        link: [
            { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' },
            { rel: "stylesheet", type: "text/css", href: "https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css" }
        ],
        script: [
            { src: 'https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js' },
            { src: 'https://code.jquery.com/jquery-3.5.1.slim.min.js' },
            { src: 'https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js' }
        ],
    },

    // Global CSS: https://go.nuxtjs.dev/config-css
    css: [
        'static/css/style.css'
    ],

    // Plugins to run before rendering page: https://go.nuxtjs.dev/config-plugins
    plugins: [
        { src: '~/plugins/vuelidate' },
    ],

    // Auto import components: https://go.nuxtjs.dev/config-components
    components: true,

    // Modules for dev and build (recommended): https://go.nuxtjs.dev/config-modules
    buildModules: [
    ],

    // Modules: https://go.nuxtjs.dev/config-modules
    modules: [
        // https://go.nuxtjs.dev/axios
        '@nuxtjs/axios',
        '@nuxtjs/auth-next',
    ],

    // Auth-next module configuration: https://auth.nuxtjs.org/
    auth: {
        strategies: {
            local: {
                scheme: 'refresh',
                token: {
                    property: 'access',
                    maxAge: 60 * 60 * 23,
                    type: 'Bearer'
                },
                refreshToken: {
                    property: 'refresh',
                    data: 'refresh',
                    maxAge: 60 * 60 * 24 * 29
                },
                endpoints: {
                    login: { url: '/api/v1/user/login', method: 'post' },
                    refresh: { url: '/api/v1/user/refresh_token', method: 'post' },
                    user: { url: '/api/v1/user/profile', method: 'get' },
                    logout: false
                },
                tokenRequired: true,
            },
        },
    },

    // Axios module configuration: https://go.nuxtjs.dev/config-axios
    axios: {
        // Workaround to avoid enforcing hard-coded localhost:3000: https://github.com/nuxt-community/axios-module/issues/308
        baseURL: 'http://127.0.0.1:4000',
    },

    // Build Configuration: https://go.nuxtjs.dev/config-build
    build: {
    }
}
