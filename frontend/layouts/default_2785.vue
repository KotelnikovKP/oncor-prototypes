<template>
    <div>
        <Navbar_2785 />
        <Nuxt />
        <Footer />
    </div>
</template>
  
  
<script>
import Navbar_2826 from "~/components/Navbar_2826";
import Footer from "@/components/Footer";

export default {
    components: {
        Navbar_2826,
        Footer,
    },
    head() {
        return {
            link: [
                { rel: "canonical", href: `http://localhost:3000${this.$route.path}` }
            ]
        }
    }
}
</script>
  
<style></style>