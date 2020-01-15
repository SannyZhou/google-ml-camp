<style scoped>
    .logo-img {
        margin: 2px 10px;
        width: 50px;
        height: 50px;
    }
    .logo-text {
        margin: 6px;
        color: white;
        font-size: x-large;
    }
    .help{
        margin: 5px;
        font-size: 15px;
        color: white;
        text-align: right;
    }
</style>


<template>
    <el-container style="height: 100%;">
        <el-header type="flex" justify="space-around" style="background-color: #545c64">
            <el-row>
                <el-col span="6">
                    <router-link to="/">
                    <img class="logo-img" src='../../static/simpson4.png'>
                    <span class="logo-text">Simpson</span>
                    </router-link>
                </el-col>
                <el-col offset="10" span="4" type='flex'>
                    <el-menu style="text-align: right" mode="horizontal" router=true :default-active="$route.path.split('/')[1]" background-color="#545c64" text-color="#fff" active-text-color="#ffd04b">
                        <el-menu-item index="upload">
                            <i class="el-icon-star-on"></i>
                            Simpson World
                        </el-menu-item>
                        <!-- <el-menu-item index="camera">
                            <i class="el-icon-star-on"></i>
                            Camera
                        </el-menu-item> -->
                    </el-menu>
                </el-col>
            </el-row>
        </el-header>
        <el-container>
            <router-view></router-view>
                <el-footer  type="flex" justify="space-around" style="background-color: #545c64; height: 38px;" >
                    <el-row type="flex" justify="end">
                        <el-col span="3px">
                            <router-link to="/about">
                                <span class="help">关于</span>
                            </router-link>
                        </el-col>
                        <el-col span="3px">
                            <router-link to="/contactus">
                                <span class="help">联系我们</span>
                            </router-link>
                        </el-col>
                    </el-row>
                </el-footer>
        </el-container>
    </el-container>
</template>

<script>
export default {
    created:function(){
        this.$message({
            message: "Welcome to Simpson's World!!"
        });
    },
    activated:function(){
    },
    methods: {
       
    }
}
</script>
