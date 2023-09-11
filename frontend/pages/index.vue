<template>
    <div class="container">
        <h1 class="my-3">Список прототипов</h1>
        <div v-if="loggedIn">
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th scope="col">#</th>
                        <th scope="col">Наименование</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td class="align-middle">2826</td>
                        <td><nuxt-link class="nav-link" to="/">Формирование комплексной человеко-читаемой выписки об основных медицинских событиях пациента на основе данных СЭМД, поступивших от разных МО, позволяющей увидеть основные вехи при оказании медицинской помощи пациентам.</nuxt-link></td>
                    </tr>
                    <tr>
                        <td class="align-middle">2785</td>
                        <td><nuxt-link class="nav-link" to="/orders_f14">[Ф14] - Предоставление обобщенных сведений о соответствии клиническим рекомендациям проведенных диагностических исследований и лечения онкологических заболеваний</nuxt-link></td>
                    </tr>
                </tbody>
            </table>
        </div>
        <div v-else>
            <h6 class="card-header"><nuxt-link to="/signin">Авторизуйтесь</nuxt-link> или <nuxt-link
                    to="/signup">зарегистрируйтесь</nuxt-link> для получения доступа к прототипам</h6>
        </div>
    </div>
</template>

<script>
import axios from "axios";
export default {
    data() {
        return {
        }
    },
    head() {
        return {
            title: "Список прототипов",
        }
    },
    methods: {
    },
    mounted() {
    },
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

<style type="text/css"></style>
