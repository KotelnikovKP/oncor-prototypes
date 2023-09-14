<template>
    <div class="container">
        <h1 class="my-3">Обобщенные сведения о соответствии клиническим рекомендациям проведенной диагностики и лечения
            пациентов</h1>

        <div v-if="loggedIn">
            <form name="report_parameters_form" @submit.prevent="reportUpdate">
                <div class="row mt-3">
                    <div class="col-md-2">
                        <div class="md-form mb-0">
                            <input type="date" id="date_from" class="form-control" placeholder="С" v-model.lazy="date_from">
                        </div>
                    </div>
                    <div class="col-md-2">
                        <div class="md-form">
                            <input type="date" id="date_to" class="form-control" placeholder="По" v-model.lazy="date_to">
                        </div>
                    </div>
                    <div class="col-md-2">
                        <div class="text-center text-md-left">
                            <button class="btn btn-primary" type="submit">Получить данные!</button>
                        </div>
                    </div>
                </div>
            </form>
            <p> </p>

            <div class="row" id="preloader" style="display: none">
                    <div class="col-md-12">
                        <img width="100em" src="/images/loading-1.gif" class="mx-auto d-block">
                    </div>
                </div>

            <table class="table table-striped">
                <thead>
                    <tr>
                        <th scope="col">#</th>
                        <th scope="col">МО</th>
                        <th scope="col">Группа</th>
                        <th scope="col">Исследование / консультация</th>
                        <th scope="col">Пациентов</th>
                        <th scope="col">Направлено</th>
                        <th scope="col">% направлено</th>
                        <th scope="col">Проведено </th>
                        <th scope="col">% проведено</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="f14_record in f14_records" :key="f14_records.row_number">
                        <td>{{ f14_record.row_number }}</td>
                        <td>{{ f14_record.mo_name }}</td>
                        <td>{{ f14_record.services_group }}</td>
                        <td><span v-for="service in f14_record.services">{{ service.service_code }}: {{ service.service_name }}<br></span></td>
                        <td>{{ f14_record.patients_count }}</td>
                        <td>{{ f14_record.referrals_count }}</td>
                        <td> </td>
                        <td>{{ f14_record.protocols_count }}</td>
                        <td> </td>
                    </tr>
                </tbody>
            </table>

            <div class="row mt-3">
                <div class="col-md-12">
                    <p class="lead">Найдено записей: {{ count_items }}</p>
                </div>
            </div>

        </div>

        <div v-else>
            <h6 class="card-header"><nuxt-link to="/signin">Авторизуйтесь</nuxt-link> или <nuxt-link
                    to="/signup">зарегистрируйтесь</nuxt-link> для получения доступа к прототипам</h6>
        </div>
    </div>
</template>

<script>
import axios from "axios";
import default_2785 from "@/layouts/default_2785";
export default {
    layout: "default_2785",
    data() {
        return {
            f14_records: [],
            count_items: 0,
            date_from: '',
            date_to: '',
        }
    },
    head() {
        return {
            title: "Обобщенные сведения о соответствии клиническим рекомендациям проведенной диагностики и лечения пациентов",
        }
    },
    methods: {
        async reportUpdate() {
            if (this.loggedIn) {
                let preloader = document.getElementById("preloader");
                preloader.style.display = "";
                try {
                    let response = await this.$axios.get(`/api/v1/orders_f14_report?date_from=${this.date_from}&date_to=${this.date_to}`);
                    this.f14_records = response.data.result;
                    this.count_items = response.data.retExtInfo.count_items;
                    preloader.style.display = "None";
                } catch ({ response }) {
                    console.log(response);
                    preloader.style.display = "None";
                }
            }
        },
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
