webpackJsonp([10],{

/***/ 400:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
Object.defineProperty(__webpack_exports__, "__esModule", { value: true });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__babel_loader_node_modules_vue_loader_lib_selector_type_script_index_0_posts_vue__ = __webpack_require__(552);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__node_modules_vue_loader_lib_template_compiler_index_id_data_v_1ee343a3_hasScoped_false_buble_transforms_node_modules_vue_loader_lib_selector_type_template_index_0_posts_vue__ = __webpack_require__(642);
function injectStyle (ssrContext) {
  __webpack_require__(664)
}
var normalizeComponent = __webpack_require__(3)
/* script */

/* template */

/* template functional */
  var __vue_template_functional__ = false
/* styles */
var __vue_styles__ = injectStyle
/* scopeId */
var __vue_scopeId__ = null
/* moduleIdentifier (server only) */
var __vue_module_identifier__ = null
var Component = normalizeComponent(
  __WEBPACK_IMPORTED_MODULE_0__babel_loader_node_modules_vue_loader_lib_selector_type_script_index_0_posts_vue__["a" /* default */],
  __WEBPACK_IMPORTED_MODULE_1__node_modules_vue_loader_lib_template_compiler_index_id_data_v_1ee343a3_hasScoped_false_buble_transforms_node_modules_vue_loader_lib_selector_type_template_index_0_posts_vue__["a" /* default */],
  __vue_template_functional__,
  __vue_styles__,
  __vue_scopeId__,
  __vue_module_identifier__
)

/* harmony default export */ __webpack_exports__["default"] = (Component.exports);


/***/ }),

/***/ 552:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//

/* harmony default export */ __webpack_exports__["a"] = ({
    data() {
        return {
            tableData: [{
                name: '上海精装学区房', //String, 名称
                description: '这是一套上海的精装学区房', //String, 描述
                location: '上海徐汇区', //String, 位置（目前还是字符串表示）
                phoneNumber: '18888888888', //String, 联系电话
                minPrice: '6万/平米', //String, 价格下限
                maxPrice: '7万/平米', //String, 价格上限
                availableTime_start: '2018-11-26T08:00:00.000Z', //Date, 可入住时间-开始，格式为2018-11-26T08:00:00.000Z
                availableTime_end: '2019-11-26T08:00:00.000Z', //Date, 可入住时间-结束，格式为2018-11-26T08:00:00.000Z
                acreage: '110平米', //String, 可用面积
                decoration: '3', //String, 装修程度：'1'-毛坯，'2'-简装，'3'-精装，'4'-豪华装
                method: '1', //String, 租赁方式：'1'-整租，'2'-合租，'3'-短租，'4'-办公
                hall: '1', //String, 几厅：'0'-零厅, '1'-一厅，'2'-两厅，'3'-三厅, '4'-四厅
                room: '2', //String, 几室：'0'-零室, '1'-一室，'2'-两室，'3'-三室, '4'-四室
                bath: '1', //String, 几卫：'0'-零卫, '1'-一卫，'2'-两卫，'3'-三卫, '4'-四卫
                imageUrl: ['www.baidu.com', 'www.qq.com'], //Array，上传图片链接列表
                others: ['WIFI', '冰箱', '洗衣机', '空调'] //Array, 家电等，例：['WIFI', '冰箱', '洗衣机']
            }, {
                name: '北京三环毛坯房', //String, 名称
                description: '这是一套北京三环的毛坯房', //String, 描述
                location: '北京', //String, 位置（目前还是字符串表示）
                phoneNumber: '13333333333', //String, 联系电话
                minPrice: '8万/平米', //String, 价格下限
                maxPrice: '10万/平米', //String, 价格上限
                availableTime_start: '2018-12-26T08:00:00.000Z', //Date, 可入住时间-开始，格式为2018-11-26T08:00:00.000Z
                availableTime_end: '2019-12-26T08:00:00.000Z', //Date, 可入住时间-结束，格式为2018-11-26T08:00:00.000Z
                acreage: '123平米', //String, 可用面积
                decoration: '1', //String, 装修程度：'1'-毛坯，'2'-简装，'3'-精装，'4'-豪华装
                method: '1', //String, 租赁方式：'1'-整租，'2'-合租，'3'-短租，'4'-办公
                hall: '1', //String, 几厅：'0'-零厅, '1'-一厅，'2'-两厅，'3'-三厅, '4'-四厅
                room: '2', //String, 几室：'0'-零室, '1'-一室，'2'-两室，'3'-三室, '4'-四室
                bath: '2', //String, 几卫：'0'-零卫, '1'-一卫，'2'-两卫，'3'-三卫, '4'-四卫
                imageUrl: ['www.baidu.com', 'www.qq.com'], //Array，上传图片链接列表
                others: ['冰箱', '洗衣机', '空调'] //Array, 家电等，例：['WIFI', '冰箱', '洗衣机']
            }],

            // 要展开的行，数值的元素是row的key值
            expands: []
        };
    },
    created() {
        this.getPosts();
    },
    methods: {
        //在<table>里，已经设置row的key值设置为每行数据id：row-key="name"
        rowClick(row, event, column) {
            Array.prototype.remove = function (val) {
                let index = this.indexOf(val);
                if (index > -1) {
                    this.splice(index, 1);
                }
            };

            if (this.expands.indexOf(row.name) < 0) {
                this.expands = [];
                this.expands.push(row.name);
            } else {
                this.expands.remove(row.name);
            }
        },

        delClick(index) {

            //发送要删除的序号
            var obj = this;
            this.$axios.delete('/api/usercenter/housing/' + this.tableData[index].id, index).then(function (res) {
                obj.$message.success('删除成功');
                obj.tableData.splice(index, 1);
            }).catch(function (err) {
                obj.$message.error('删除失败');
            });
        },
        getPosts() {
            var obj = this;
            this.$axios.get('/api/usercenter/housing/view').then(function (res) {
                obj.tableData = res.data;
                obj.$message.success('载入成功');
            }).catch(function (err) {
                obj.$message.error('载入失败');
            });
        },
        toForm() {
            this.$router.push('/form');
        }
    }

});

/***/ }),

/***/ 566:
/***/ (function(module, exports, __webpack_require__) {

exports = module.exports = __webpack_require__(8)(undefined);
// imports


// module
exports.push([module.i, ".demo-table-expand{font-size:0}.demo-table-expand label{width:90px;color:#99a9bf}.demo-table-expand .el-form-item{margin-right:0;margin-bottom:0;width:50%}", ""]);

// exports


/***/ }),

/***/ 642:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
var render = function () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('el-main',[_c('el-table',{staticStyle:{"width":"100%"},attrs:{"data":_vm.tableData,"row-key":"name","expand-row-keys":_vm.expands},on:{"row-click":_vm.rowClick}},[_c('el-table-column',{attrs:{"type":"expand"},scopedSlots:_vm._u([{key:"default",fn:function(props){return [_c('el-form',{staticClass:"demo-table-expand",attrs:{"label-position":"left","inline":""}},[_c('el-form-item',{attrs:{"label":"名称"}},[_c('span',[_vm._v(_vm._s(props.row.name))])]),_vm._v(" "),_c('el-form-item',{attrs:{"label":"描述"}},[_c('span',[_vm._v(_vm._s(props.row.description))])]),_vm._v(" "),_c('el-form-item',{attrs:{"label":"位置"}},[_c('span',[_vm._v(_vm._s(props.row.location))])]),_vm._v(" "),_c('el-form-item',{attrs:{"label":"联系电话"}},[_c('span',[_vm._v(_vm._s(props.row.phoneNumber))])]),_vm._v(" "),_c('el-form-item',{attrs:{"label":"价格下限"}},[_c('span',[_vm._v(_vm._s(props.row.minPrice))])]),_vm._v(" "),_c('el-form-item',{attrs:{"label":"价格上限"}},[_c('span',[_vm._v(_vm._s(props.row.maxPrice))])]),_vm._v(" "),_c('el-form-item',{attrs:{"label":"入住开始"}},[_c('span',[_vm._v(_vm._s(props.row.availableTime_start))])]),_vm._v(" "),_c('el-form-item',{attrs:{"label":"入住结束"}},[_c('span',[_vm._v(_vm._s(props.row.availableTime_end))])]),_vm._v(" "),_c('el-form-item',{attrs:{"label":"可用面积"}},[_c('span',[_vm._v(_vm._s(props.row.acreage))])]),_vm._v(" "),_c('el-form-item',{attrs:{"label":"家电配置"}},[_c('span',[_vm._v(_vm._s(props.row.decoration))])]),_vm._v(" "),_c('el-form-item',{attrs:{"label":"租赁方式"}},[_c('span',[_vm._v(_vm._s(props.row.method))])]),_vm._v(" "),_c('el-form-item',{attrs:{"label":"几厅"}},[_c('span',[_vm._v(_vm._s(props.row.hall))])]),_vm._v(" "),_c('el-form-item',{attrs:{"label":"几室"}},[_c('span',[_vm._v(_vm._s(props.row.room))])]),_vm._v(" "),_c('el-form-item',{attrs:{"label":"几卫"}},[_c('span',[_vm._v(_vm._s(props.row.bath))])]),_vm._v(" "),_c('el-form-item',{attrs:{"label":"图片"}},[_c('span',_vm._l((props.row.images),function(image,index){return _c('img',{key:index,attrs:{"src":image,"height":"180","width":"200"}})}))]),_vm._v(" "),_c('el-form-item',{attrs:{"label":"其他"}},[_c('span',[_vm._v(_vm._s(props.row.others))])])],1)]}}])}),_vm._v(" "),_c('el-table-column',{attrs:{"label":"名字","prop":"name"}}),_vm._v(" "),_c('el-table-column',{attrs:{"label":"位置","prop":"location"}}),_vm._v(" "),_c('el-table-column',{attrs:{"label":"可用面积","prop":"acreage"}}),_vm._v(" "),_c('el-table-column',{attrs:{"label":"最低价格","prop":"minPrice"}}),_vm._v(" "),_c('el-table-column',{attrs:{"label":"联系方式","prop":"phoneNumber"}}),_vm._v(" "),_c('el-table-column',{attrs:{"label":"操作","prop":"oper"},scopedSlots:_vm._u([{key:"default",fn:function(scope){return [_c('el-button',{attrs:{"type":"primary"},on:{"click":function($event){$event.stopPropagation();_vm.delClick(scope.$index)}}},[_vm._v("删除")])]}}])})],1),_vm._v(" "),_c('el-button',{staticStyle:{"margin":"5px"},attrs:{"type":"primary"},on:{"click":_vm.toForm}},[_vm._v("新发布")])],1)}
var staticRenderFns = []
var esExports = { render: render, staticRenderFns: staticRenderFns }
/* harmony default export */ __webpack_exports__["a"] = (esExports);

/***/ }),

/***/ 664:
/***/ (function(module, exports, __webpack_require__) {

// style-loader: Adds some css to the DOM by adding a <style> tag

// load the styles
var content = __webpack_require__(566);
if(typeof content === 'string') content = [[module.i, content, '']];
if(content.locals) module.exports = content.locals;
// add the styles to the DOM
var update = __webpack_require__(10)("4b8918f2", content, true);

/***/ })

});
//# sourceMappingURL=10.js.map?8a57330b40825d85feec