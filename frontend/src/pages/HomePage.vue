<template>
  <div class="flex flex-col">
    <Header />
    <div class="p-3 gap-3 flex flex-row">
      <SidebarComponent />
      <div class="flex-grow">
        <Card>
          <template #title> Homepage </template>
          <template #content>
            <div
              v-if="projects?.length"
              class="grid grid-cols-[repeat(auto-fill,minmax(12rem,1fr))] md:grid-cols-[repeat(auto-fill,minmax(17rem,1fr))] gap-3"
            >
              <template v-for="proj in projects" :key="proj.name">
                <Transformer
                  :title="proj.name"
                  :description="proj.description"
                  :in="[]"
                  :out="[]"
                  @click="
                    () =>
                      router.push({
                        name: 'ProjectSites',
                        params: {
                          proj: proj.name,
                        },
                      })
                  "
                />
              </template>
            </div>
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import Header from '@/components/HeaderComponent.vue'
import { useAuthenticated } from '@/backend/security'
import { watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SidebarComponent from '@/components/SidebarComponent.vue'
import Transformer from '@/components/TransformerComponent.vue'
import { useProjectList } from '@/backend/projects'

const { data: authenticated } = useAuthenticated()
const router = useRouter()
const route = useRoute()
watch(
  authenticated,
  () => {
    if (!authenticated.value) {
      router.push({
        name: 'Login',
        query: {
          redirect: route.fullPath,
        },
      })
    }
  },
  { immediate: true },
)

const { data: projects } = useProjectList()
</script>

<style scoped></style>
