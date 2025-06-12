const ev = {
        __name: "App", setup(e) {
            let t = !1;
            const n = ot(null), 
                s = ot(0), 
                r = ot(0), 
                i = C => {s.value = C.touches[0].clientX}, 
                o = C => {r.value = C.changedTouches[0].clientX;
                const P = r.value - s.value;
                P > 50 ? Z(-1) : P < -50 && Z(1)
            }, a = ot(!1), l = () => {
                a.value = !1
            }, u = ot(!1), c = ot({});

            function d(C, P, K, nt, ht, Gt) {
                c.value = {
                    lesson_name: C,
                    teacher_name: P,
                    classroom: K,
                    start_time: nt,
                    end_time: ht,
                    tag: Gt
                }, u.value = !0
            }

            function p() {
                u.value = !1
            }

            const _ = {
                "08:00": "1",
                "08:55": "2",
                "10:00": "3",
                "10:45": "4",
                "12:30": "午1",
                "13:25": "午2",
                "14:30": "5",
                "15:25": "6",
                "16:30": "7",
                "17:25": "8",
                "19:30": "9",
                "20:25": "10",
                "21:20": "11"
            }, E = {
                "08:45": "1",
                "09:40": "2",
                "10:45": "3",
                "11:40": "4",
                "13:15": "午1",
                "14:10": "午2",
                "15:15": "5",
                "16:10": "6",
                "17:15": "7",
                "18:10": "8",
                "20:15": "9",
                "21:10": "10",
                "22:05": "11"
            }, b = ot(0), v = ot([{
                week: "请更新数据",
                start_date: "19700101",
                end_date: "19700107",
                per_day_lessons: {
                    19700101: [],
                    19700102: [],
                    19700103: [],
                    19700104: [],
                    19700105: [],
                    19700106: [],
                    19700107: []
                }
            }]);

            function R(C) {
                return ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][C % 7]
            }

            function k(C) {
                const P = C.slice(-4), K = P.slice(0, 2), nt = P.slice(2);
                return `${K}-${nt}`
            }

            function D(C, P) {
                return `${C}_${P}`
            }

            function y(C) {
                const P = Object.keys(_)[C - 1], K = Object.keys(E)[C - 1];
                return `${_[P]}<br/>${P}-${K}`
            }

            function I(C, P) {
                const K = Object.keys(_).indexOf(C);
                return Object.keys(E).indexOf(P) - K + 1
            }

            function j() {
                const C = ["255,69,0", "0,255,127", "255,223,0", "255,165,0", "30,144,255", "238,130,238", "255,105,180", "135,206,250", "173,255,47", "0,255,255"];
                return C[Math.floor(Math.random() * C.length)]
            }

            function U(C) {
                let P = C.target.closest(".lesson"), K = P.getAttribute("data-lesson-name"),
                    nt = P.getAttribute("data-teacher"), ht = P.getAttribute("data-classroom"),
                    Gt = P.getAttribute("data-start"), f = P.getAttribute("data-end"), h = P.getAttribute("data-tag");
                d(K, nt, ht, Gt, f, h)
            }

            function J() {
                document.querySelectorAll("div.lesson").forEach(P => {
                    P.removeEventListener("click", U), P.remove()
                })
            }

            function Z(C) {
                const P = b.value;
                if (P + C < 0 || P + C >= v.value.length) {
                    n.value.showToast("前面的区域，以后再来探索吧", "secondary");
                    return
                }
                b.value = P + C, mt()
            }

            function et(C) {
                C.addEventListener("click", U)
            }

            function ut(C, P, K, nt) {
                const ht = document.getElementById(`${P + 1}_${K + 1}`), Gt = document.getElementById(`${P + 1}_${K + nt}`),
                    f = document.getElementById("calendar");
                let h = ht.getBoundingClientRect(), g = Gt.getBoundingClientRect(), O = h.top, w = h.left, A = g.bottom,
                    L = g.right, N = f.getBoundingClientRect().top;
                const x = Math.abs(L - w), S = Math.abs(A - O), $ = document.createElement("div");
                $.className = "lesson", $.style.position = "absolute", $.style.top = `${O - N}px`, $.style.left = `${w}px`, $.style.width = `${x}px`, $.style.height = `${S}px`, $.style.backgroundColor = C.lesson_disabled ? "rgba(128,128,128)" : `rgb(${j()})`, $.style.border = "2px solid #fff", $.style.borderRadius = "10px", $.style.zIndex = "10", $.style.padding = "5px", $.style.overflow = "hidden", $.style.fontSize = window.innerWidth <= 576 ? "0.6rem" : "1rem", $.classList.add("text-white"), $.setAttribute("data-lesson-name", C.lesson_name), $.setAttribute("data-teacher", C.teacher_name), $.setAttribute("data-classroom", C.classroom), $.setAttribute("data-start", C.start_time), $.setAttribute("data-end", C.end_time), $.setAttribute("data-tag", C.tag), $.innerHTML = `
    <p class="lesson-name">${C.lesson_name}${C.tag != "" ? `(${C.tag})` : ""} - ${C.classroom}</p>
  `, document.getElementById("calendar").appendChild($), et($)
            }

            function mt() {
                J(), Object.entries(v.value[b.value].per_day_lessons).forEach(([C, P], K) => {
                    P.forEach((nt, ht) => {
                        const Gt = Object.keys(_).indexOf(nt.start_time), f = I(nt.start_time, nt.end_time);
                        ut(nt, K, Gt, f)
                    })
                })
            }

            hr(() => {
                console.log("DOM 更新完成，开始执行特定函数"), mt(), document.querySelectorAll("div.lesson").forEach(C => {
                    et(C)
                })
            });
            const ft = ot(null);

            function Ft() {
                ft.value && ft.value.loadCaptchaImage()
            }

            const Ht = ot(null);

            function tt() {
                var C;
                (C = Ht.value) == null || C.open()
            }

            const Y = ot(null);

            async function X() {
                try {
                    const C = await dt.get(`/api/jw/check_session_avail`);
                    Y.value = C.data.success, n.value.showToast("登录成功！")
                } catch {
                    Y.value = !1, n.value.showToast("登录失效", "danger")
                }
            }

            const bt = ot([]), Lt = ot(0);

            function jt(C) {
                C = String(C);
                const P = C.slice(0, 4), K = C.slice(4), nt = String(Number(P) + 1);
                let ht = "";
                return K === "1" ? ht = "上半学期" : K === "2" ? ht = "下半学期" : ht = "未知学期", `${P}-${nt} ${ht}`
            }

            function Et() {
                !1 && fetch(`/api/jw/fetch_lessons`, {
                    method: "POST",
                    headers: {"Content-Type": "application/x-www-form-urlencoded"},
                    credentials: "include"
                }).then(C => C.json()).then(C => {
                    C.success ? (n.value.showToast("重置成功！"), se()) : n.value.showToast(C.msg, "danger")
                }).catch(C => n.value.showToast("重置失败，请重试", "danger"))
            }

            function ve() {
                t && fetch(`/api/jw/update_lessons`, {
                    method: "POST",
                    headers: {"Content-Type": "application/x-www-form-urlencoded"},
                    credentials: "include"
                }).then(C => C.json()).then(C => {
                    C.success ? (n.value.showToast(C.msg), $t()) : n.value.showToast(C.msg, "danger")
                }).catch(C => n.value.showToast("更新失败，请重试", "danger"))
            }

            function se() {
                dt.get(`/api/local/get_all_term_id`).then(C => {
                    bt.value = C.data.data, C.data.data != [] && (t = !0), $t()
                }).catch(C => {
                    n.value.showToast("获取失败，请重试", "danger"), console.error("请求错误:", C)
                })
            }

            function $t() {
                t && dt.get(`/api/local/get_calendar?term_id=${bt.value[Lt.value]}`).then(C => {
                    v.value = C.data.data;
                    const P = VE(v);
                    b.value = P == -1 ? 0 : P, mt()
                }).catch(C => {
                    n.value.showToast("获取失败，请重试", "danger"), console.error("请求错误:", C)
                })
            }

            return Is(Lt, (C, P) => {
                $t()
            }), X(), se(), (C, P) => (pt(), _t(Tt, null, [a.value ? (pt(), _t("div", {
                key: 0,
                class: "overlay",
                onClick: l
            })) : gn("", !0), Qt(Op, {
                ref_key: "captchaRef",
                ref: ft,
                onLoginSuccess: X
            }, null, 512), Qt(HE, {ref_key: "editorRef", ref: Ht}, null, 512), Qt(RE, {
                ref_key: "toastRef",
                ref: n
            }, null, 512), F("div", {class: "d-flex flex-column vh-100"}, [F("div", {class: "header d-flex justify-content-between align-items-center py-1 px-2 bg-success text-white flex-shrink-0"}, [F("button", {
                onClick: P[0] || (P[0] = K => a.value = !a.value),
                class: "btn btn-md text-white"
            }, "更多选项"), F("div", null, [F("button", {
                onClick: P[1] || (P[1] = K => Z(-1)),
                class: "btn btn-md text-white me-2"
            }, "上一周"), F("button", {
                onClick: P[2] || (P[2] = K => Z(1)),
                class: "btn btn-md text-white mx-2"
            }, "下一周")]), P[5] || (P[5] = F("a", {href: "https://ntkk.net"}, [F("button", {class: "btn btn-md text-white me-2"}, "NTKK")], -1))]), a.value ? (pt(), _t("div", {key: 0, class: "left-window d-flex flex-column justify-content-between"}, [F("div", {class: "content text-center"}, [F("ul", {class: "list-unstyled"}, [F("li", null, [F("button", {
                onClick: l,
                class: "btn btn-md text-white"
            }, "返回")]), F("li", null, [F("button", {
                onClick: ve,
                class: "btn btn-md text-white"
            }, "更新调补课信息")]), F("li", null, [F("button", {
                onClick: Et,
                class: "btn btn-md text-white"
            }, "重置所有课程表")]), F("li", null, [P[6] || (P[6] = Ms(" 学期： ")), Xn(F("select", {
                "onUpdate:modelValue": P[3] || (P[3] = K => Lt.value = K),
                class: "form-select"
            }, [(pt(!0), _t(Tt, null, _n(bt.value, (K, nt) => (pt(), _t("option", {
                key: K,
                value: nt
            }, vt(jt(K)), 9, ["value"]))), 128))], 512), [[Md, Lt.value]])])])]), F("div", {class: "login-section text-center mt-3"}, [F("button", {
                class: "btn btn-md text-white",
                onClick: tt
            }, "编辑账号密码"), F("button", {
                class: "btn btn-md text-white",
                onClick: Ft
            }, "登录账户"), Y.value !== null ? (pt(), _t("div", {
                key: 0,
                class: fs(Y.value ? "text-success mt-2" : "text-danger mt-2")
            }, vt(Y.value ? "已登录教务系统" : "未登录教务系统"), 3)) : gn("", !0), P[7] || (P[7] = F("div", null, [F("a", {href: "https://ntkk.net/d/1241"}, "版本号：Beta 0.1")], -1))])])) : gn("", !0), u.value ? (pt(), _t("div", Ul({key: 1}, c.value, {
                class: "modal-overlay",
                onClick: p
            }), [F("div", {
                class: "modal-content", onClick: P[4] || (P[4] = Hd(() => {
                }, ["stop"]))
            }, [F("p", null, "课程：" + vt(c.value.lesson_name), 1), F("p", null, "教师：" + vt(c.value.teacher_name), 1), F("p", null, "教室：" + vt(c.value.classroom), 1), F("p", null, "时间：" + vt(c.value.start_time) + " - " + vt(c.value.end_time), 1), F("p", null, "标签：" + vt(c.value.tag || "无"), 1), F("button", {
                onClick: p,
                class: "btn btn-lg bg-secondary text-white"
            }, "关闭")])], 16)) : gn("", !0), F("div", {
                id: "calendar",
                class: "flex-grow-1 overflow-auto",
                style: {position: "relative"},
                onTouchstart: i,
                onTouchend: o
            }, [F("table", {
        class: "table text-center table-striped table-responsive",
        style: {"table-layout": "fixed", width: "100%", "align-items": "stretch"}
    }, [F("thead", {class: "table-dark", style: {"vertical-align": "middle"}}, [F("tr", null, [F("th", {class: "fs-7", style: {width: "10%"}}, " 第 " + vt(v.value[b.value].week) + " 周 ", 1), (pt(!0), _t(Tt, null, _n(v.value[b.value].per_day_lessons, (K, nt, ht) => (pt(), _t("th", {
                key: nt,
                class: "fs-7",
                style: {width: "12.85%"}
            }, [Ms(vt(R(ht)), 1), P[8] || (P[8] = F("br", null, null, -1)), Ms(vt(k(nt)), 1)]))), 128))])]), F("tbody", null, [(pt(), _t(Tt, null, _n(13, K => F("tr", {
                key: "row-" + K,
                id: "lesson_" + K,
                class: "h-auto"
            }, [F("td", {
                innerHTML: y(K),
                class: "text-truncate fs-7"
            }, null, 8, innerHTML), (pt(), _t(Tt, null, _n(7, nt => F("td", {
                key: "day-" + nt,
                id: D(nt, K),
                class: "text-truncate fs-7"
            }, P[9] || (P[9] = [F("p", null, null, -1)]), 8, ["id"])), 64))], 8, ["id"])), 64))])])], 32)])], 64))
        }
    }, nv = Xi(ev, [["__scopeId", "data-v-5fe0da6e"]]);