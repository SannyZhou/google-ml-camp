const Router = [
    {
        path: '/',
        redirect: 'index',
        meta: {
            title: 'Simpson World'
        },
        component: (resolve) => require(['./views/main.vue'], resolve),
        children: [
            {
                path: 'index',
                meta: {
                    title: 'index',
                },
                component: (resolve) => require(['./views/index.vue'], resolve)
            },
        ]
    }
]
export default Router;
