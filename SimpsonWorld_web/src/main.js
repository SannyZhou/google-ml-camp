import Vue from 'vue'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import App from './App.vue'
import VueRouter from 'vue-router'
import Routers from './router'
import axios from 'axios'
import Datatable from 'vue2-datatable-component'


Vue.use(Datatable)
Vue.use(VueRouter)
Vue.use(ElementUI)
Vue.config.devtools = true;


const RouterConfig = {
    mode: 'history',
    routes: Routers
}
const router = new VueRouter(RouterConfig)


Vue.prototype.$axios = axios



new Vue({
    el: '#app',
    router: router,
    render: h => h(App)
})
