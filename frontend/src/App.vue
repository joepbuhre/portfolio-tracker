<template>
    <TheHeader />
    <div class="px-10 pb-10">
        <router-view />
    </div>
</template>

<script setup lang="ts">
import TheHeader from './components/TheHeader.vue';
</script>

<style lang="postcss">
body {
    @apply bg-slate-50 bg-opacity-10
}
</style>