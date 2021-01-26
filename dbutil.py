import sqlite3


class DBHelper:
    def __init__(self, dbname="todo.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)
        # self.conn = self.con.cursor()

    def setup(self):
        stmt = "CREATE TABLE IF NOT EXISTS items (id, goal,income,invest,expances,CC_bills,Ac_balance,m_invest,m_expences,m_CC_bills)"
        self.conn.execute(stmt)
        self.conn.commit()

    def update_item(self,x,y,z):
        print(x,y)
        # stmt = "INSERT INTO items (%s) VALUES (?)"
        stmt="UPDATE items SET (%s) = (?) WHERE id = ?" % (x)
        args = (y,z,)
        self.conn.execute(stmt,args)
        self.conn.commit()
    def add_id(self,x,y):
        stmt="insert into items (%s) SELECT (?) WHERE not exists(select * from items where id=(?))" % (x)
        # stmt = "INSERT INTO items (%s) VALUES (?)"
        args = (y,y,)
        self.conn.execute(stmt ,args)
        self.conn.commit()

    def delete_item(self, id):
        stmt = "DELETE FROM items WHERE id = (?)"
        args = (id, )
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_items(self,col,id):
        stmt = "SELECT (%s) FROM items WHERE id = (?)" % (col)
        args = (id, )
        return [x[0] for x in self.conn.execute(stmt,args)]
      
