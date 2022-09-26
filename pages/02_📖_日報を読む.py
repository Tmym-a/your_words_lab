import streamlit as st
import module


class Page2(module.Page):
    def get_data(self):
        df = self.cor.get_reports_df() # 委譲

        if self.authority:
            input_users = st.multiselect('ユーザー名でフィルター', self.users) 
            
            if not input_users:
                user_df = df
            else:
                user_df = df.query('writer in @input_users')    
        else:
            input_users = [self.user]           
            user_df = df[df['writer']==self.user]

        desc_user_df = user_df.sort_values('date', ascending=False)
        reports = desc_user_df.loc[:, ['date','writer','words']]

        return input_users, user_df, reports

    def main(self):
        st.title('Daily Reports')
        try:
            input_users, user_df, reports = self.get_data()

            # 折れ線グラフの表示
            if len(input_users) == 1 and len(reports) > 1:
                chart_df = user_df.loc[:, ['date','feelings','variables']].head(30)
                chart_df = chart_df.set_index('date')
                st.write('数値の推移')
                st.line_chart(chart_df)
            # テーブルの表示
            st.write('日報')
            st.table(reports.head(30))

        except KeyError:
            st.warning('まだ何も書いてありません')


cor = module.Corpus()
page = Page2(cor)

page.check_login_status()
    


