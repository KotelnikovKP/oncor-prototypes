<template>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark sticky-top">
        <nuxt-link class="navbar-brand" to="/diagnosis-registers">
            <img src="/favicon.ico" width="30" height="30" alt="logo">
        </nuxt-link>
        <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent"
            aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarSupportedContent">
            <ul class="navbar-nav mr-auto">
                <!-- <li class="nav-item active">
                    <nuxt-link class="nav-link" to="/diagnosis-registers">Список регистров ССЗ</nuxt-link>
                </li> -->
                <li class="nav-item">
                    <nuxt-link class="nav-link" to="/">Возврат к списку прототипов</nuxt-link>
                </li>
            </ul>
            <span class="navbar-text mr-2" v-if="user">{{user.username}}</span>
            <span v-if="loggedIn"><nuxt-link class="btn btn-outline-light mr-2" to="/signout">Выход</nuxt-link></span>
            <span v-else>
                <nuxt-link class="btn btn-outline-light mr-2" to="/signin">Вход</nuxt-link>
                <nuxt-link class="btn btn-outline-light mr-2" to="/signup">Регистрация</nuxt-link>
            </span>
        </div>
    </nav>
</template>
  
<script>
export default {
    name: "Navbar",
    computed: {
        loggedIn() {
            return this.$auth.loggedIn
        },
        user() {
            return this.$auth.user
        },
        token() {
            return this.$auth.strategy.token.get()
        }
    }
}
</script>
  
<style scoped></style>