<template>
    <TheLoginModel v-if="showLogin" @success="loginSuccess" class="z-50" />
    <header class="sticky top-0 bg-white">
        <nav class="flex px-10 py-2 shadow-md">
            <div class="w-1/12" v-for="loc in routes">
                <RouterLink :to="loc">
                    {{ loc.name }}
                </RouterLink>
            </div>
            <button class="fixed top-2 right-2 flex gap-2" @click="logout">
                <LogOutIcon />
                Logout
            </button>
        </nav>
    </header>
</template>
<script setup lang="ts">
import { ref } from "vue";
import { RouteLocationNamedRaw, RouteLocationRaw } from "vue-router";
import {LogOutIcon} from 'lucide-vue-next'
import { useMain } from "../store/main";
import TheLoginModel from "./TheLoginModel.vue";

const main = useMain()

const logout = () => {
    showLogin.value = true
    main.setUserId(null)
}

const showLogin = ref<boolean>(true);

const loginSuccess = () => {
    showLogin.value = false 
}


const routes = ref<RouteLocationNamedRaw[]>([
    {
        name: 'Home'
    },
    {
        name: "Portfolio",
    },
    {
        name: "Prestaties",
    },
]);
</script>
