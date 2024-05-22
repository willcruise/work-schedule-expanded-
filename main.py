import numpy as np
import calendar
import datetime


#get year and month of the making schedule
print("Enter year and month: year-month ex)2024-3")
yearmonth = input()

#get monthrange and first day of week of the month
datelist = yearmonth.replace(" ", "").split("-")
datetime_date = datetime.date(int(datelist[0]), int(datelist[1]), 1)

dayofweek = datetime_date.weekday()
monthrange = calendar.monthrange(int(datelist[0]), int(datelist[1]))[1]

#get holidays
print("Enter the holidays: day1, day2, ... ex)4,5,6,15,29")
holidaysinput = input()
holidaysinput = holidaysinput.replace(" ","").split(",")
holidays = []
for i in holidaysinput:
  if i != '':
    holidays.append(int(i))

#dutytypes
dutytypes = ['평야', '금야', '토주야', '일주야']

# make calendar
def makecalen(dayofweek, monthrange):
  calen = {}
  #set initial dutytypes regarding to day of week
  for i in range(1, monthrange + 1):
    calen[i] = []
    if dayofweek == 0:
      calen[i].append(dayofweek)
      calen[i].append('월')
    elif dayofweek == 1:
      calen[i].append(dayofweek)
      calen[i].append('화')
    elif dayofweek == 2:
      calen[i].append(dayofweek)
      calen[i].append('수')
    elif dayofweek == 3:
      calen[i].append(dayofweek)
      calen[i].append('목')
    elif dayofweek == 4:
      calen[i].append(dayofweek)
      calen[i].append('금')
    elif dayofweek == 5:
      calen[i].append(dayofweek)
      calen[i].append('토')
    else:
      calen[i].append(dayofweek)
      calen[i].append('일')

    if dayofweek < 6:
      dayofweek += 1
    else : dayofweek = 0

  return calen

calen = makecalen(dayofweek, monthrange)


#get workers
print("Enter the workers for guardroom: name1, name2, ...")
workersguard = input()
workersguard = workersguard.replace(" ","").split(",")

print("Enter the workers for operators: name1, name2, ...")
workersop = input()
workersop = workersop.replace(" ","").split(",")

print("Enter the workers for cq: name1, name2, ...")
workerscq = input()
workerscq = workerscq.replace(" ","").split(",")

print("Enter the workers for vigil: name1, name2, ...")
workersvigil = input()
workersvigil = workersvigil.replace(" ","").split(",")

print("Enter the workers for runner: name1, name2, ...")
workersguard = input()
workersguard = workersguard.replace(" ","").split(",")


#get dayoffs
print("Enter the dayoffs of workers; name1: day1 ~ day2, day3, name2: ...")
dayoffs = input()

#process the dayoff string to necessary form
def processdayoff(dayoffs):
  dayoffs = dayoffs.replace(' ', '').split(':')

  if dayoffs != ['']:
    for ind in range(len(dayoffs)):
      dayoffs[ind] = dayoffs[ind].split(',')

    draft = {}
    for ind in range(len(dayoffs)-2):
      draft[dayoffs[ind][-1]] = dayoffs[ind+1][:-1]
    draft[dayoffs[-2][-1]] = dayoffs[-1]

    draft2 = {}
    for vacationer in draft:
      draft2[vacationer] = []
      for block in draft[vacationer]:
        if '~' not in block:
          draft2[vacationer].append(int(block))
        else:
          bound = block.split('~')
          for date in range(int(bound[0]), int(bound[1])+1):
            draft2[vacationer].append(date)

  else: draft2 = {}

  result = {}
  for date in range(1, monthrange+1):
    result[date] = []

  for vacationer in draft2:
    for date in draft2[vacationer]:
      result[date].append(vacationer)

  return result

dayoffs = processdayoff(dayoffs)

# constants: monthrange, holidays, dutytypes, weights, row, col
def maketable1(workers, dutytypes, calen):

  #initialize table for alloting workers
  row = len(workers)
  col = monthrange

  #initialize table for matching dutytype for each days
  dayanddutytype = np.zeros((monthrange, len(dutytypes)))
  for r in range(monthrange):
    for c in range(len(dutytypes)):
      if dutytypes[c] == calen[r+1][2] :
        dayanddutytype[r, c] = 1

  #match workers and column
  wmatch = {}
  for i in range(len(workers)):
    wmatch[i] = workers[i]
    wmatch[workers[i]] = i

  #match dutytype and index(column)
  dmatch = {}
  for i in range(len(dutytypes)):
    dmatch[i] = dutytypes[i]
    dmatch[dutytypes[i]] = i

  #generate weightstate of each column(worker) of table
  def genweightstate(table):
    weightstate = np.matmul(table, dayanddutytype)

    return weightstate

  #return column(worker) of minimum weight sum
  def getmins(weightstate, dutytype):
    col = dmatch[dutytype]
    result = []
    value = -1
    for r in range(len(weightstate)):
      if value == -1:
        value = weightstate[r, col]
        result.append(r)
      else:
        if value < weightstate[r, col] : continue
        elif value > weightstate[r, col]:
          result.clear()
          result.append(r)
          value = weightstate[r, col]
        else: result.append(r)

    return result

  #return latest day the work is done
  def getlatest(table, row):
    for col in reversed(range(monthrange)):
      if table[row,col] == 1: return col
    else: return -1

  #allot worker to table of column
  def allotworker(tabledraft, col):
    #get weightstate of table; weightstate is a indicater for
    #checking the amount of work done to date by each worker
    weightstate = genweightstate(tabledraft)

    #rows(workers) that are not excluded by dayoffs
    availablerows = len(weightstate)

    #concern dayoffs : set data value of the dayoff worker(row) to 128(large)
    for w in dayoffs[col+1]:
      r = wmatch[w]
      for c in range(len(weightstate[r])):
        weightstate[r, c] = 128
        availablerows -= 1

    # exclude previous worker row from weightstate if rows are more than one
    if availablerows > 1:
      previousworker = -1
      for r in range(len(tabledraft)):
        if tabledraft[r, col-1] == 1:
          previousworker = r
          break

      for c in range(len(weightstate[previousworker])):
        weightstate[previousworker, c] = 128


    #get final candadites from weightstate by picking worker who has done minimum work
    candidates = getmins(weightstate, calen[col+1][2])

    #pick one worker which the day of latest work is farthest from candidates
    minval = len(tabledraft[0])
    finalcandidate = []
    for candidate in candidates:
      test = getlatest(tabledraft, candidate)
      if minval < test: continue
      elif minval > test:
        finalcandidate.clear()
        finalcandidate.append(candidate)
        minval = test
      else: finalcandidate.append(candidate)

    tabledraft[finalcandidate[0],col] = 1

    return tabledraft

  #iterate through columns of table, allot worker, and render final table
  table = np.zeros((row, col), dtype = np.int8)
  for itercol in range(col):
    table = allotworker(table, itercol)

  return table
'''
  def schedulelog(table):
    log = {}
    for w in workers:
      log[w] = {}
      for d in dutytypes:
        tmp = {d:0}
        log[w].update(tmp)

    for r in range(len(table)):
      for c in range(len(table[r])):
        if table[r, c] == 1:
          for d in dutytypes:
            if calen[c+1][2] == d: log[wmatch[r]][d] += 1

    print('<schedule log>')
    for w in log:
      print(w, ':', log[w])

  schedulelog(table)
'''

def maketable2(workers, dutytypes, calen):
  #tables by duty
  tables = []

  row = len(workers)
  col = monthrange
  #initialize table for alloting workers
  for d in dutytypes:
    tables.append(np.zeros((row, col), dtype = np.int8))

  def maketable2draft(workers, calen, pretable):

    dayanddutytype = np.ones((monthrange, 1))

    #match workers and column
    wmatch = {}
    for i in range(len(workers)):
      wmatch[i] = workers[i]
      wmatch[workers[i]] = i

  
    #generate weightstate of each column(worker) of table
    def genweightstate(table):
      weightstate = np.matmul(table, dayanddutytype)

      return weightstate

    #return column(worker) of minimum weight sum
    def getmins(weightstate):
      col = 0
      result = []
      value = -1
      for r in range(len(weightstate)):
        if value == -1:
          value = weightstate[r, col]
          result.append(r)
        else:
          if value < weightstate[r, col] : continue
          elif value > weightstate[r, col]:
            result.clear()
            result.append(r)
            value = weightstate[r, col]
          else: result.append(r)

      return result

    #return latest day the work is done
    def getlatest(table, row):
      for col in reversed(range(monthrange)):
        if table[row,col] == 1: return col
      else: return -1

    #allot worker to table of column
    def allotworker(tabledraft, col):
      #get weightstate of table; weightstate is a indicater for
      #checking the amount of work done to date by each worker
      weightstate = genweightstate(tabledraft)

      #rows(workers) that are not excluded by dayoffs
      availablerows = len(weightstate)

      #concern dayoffs : set data value of the dayoff worker(row) to 128(large)
      for w in dayoffs[col+1]:
        r = wmatch[w]
        for c in range(len(weightstate[r])):
          weightstate[r, c] = 128
          availablerows -= 1

      # exclude previous worker row from weightstate if rows are more than one
      if availablerows > 1:
        previousworker = -1
        for r in range(len(tabledraft)):
          if tabledraft[r, col-1] == 1:
            previousworker = r
            break

        for c in range(len(weightstate[previousworker])):
          weightstate[previousworker, c] = 128


      #get final candadites from weightstate by picking worker who has done minimum work
      candidates = getmins(weightstate)

      #pick one worker which the day of latest work is farthest from candidates
      minval = len(tabledraft[0])
      finalcandidate = []
      for candidate in candidates:
        test = getlatest(tabledraft, candidate)
        if minval < test: continue
        elif minval > test:
          finalcandidate.clear()
          finalcandidate.append(candidate)
          minval = test
        else: finalcandidate.append(candidate)

      tabledraft[finalcandidate[0],col] = 1

      return tabledraft

    #iterate through columns of table, allot worker, and render final table
    table = np.zeros((row, col), dtype = np.int8)
    for itercol in range(col):
      table = allotworker(table, itercol)

    return table


#dutytypes for op
dutytypesop = ['평야', '금야', '토주야', '일주야']
# modify the dutytype regarding holidays
def modifycalop(calendraft, dutytypes):
  for i in holidays:
    calendraft[i][0] = 5

  yesteroff = False
  for i in calendraft:
    if calendraft[i][0] == 5 or calendraft[i][0] == 6:
      if yesteroff == True: calendraft[i][0] = 6
      yesteroff = True
    else: yesteroff = False


  for i in calendraft:
    if  calendraft[i][0] <= 3:
      calendraft[i].append(dutytypes[0])
    elif calendraft[i][0] == 4:
      calendraft[i].append(dutytypes[1])
    elif calendraft[i][0] == 5:
      calendraft[i].append(dutytypes[2])
    elif calendraft[i][0] == 6:
      calendraft[i].append(dutytypes[3])

  return calen

calenop = modifycalop(calen, dutytypesop)
#table for operators
tableop = maketable1(workersop, dutytypesop, calen)

#dutytypes for cq
dutytypescq = ['평당', '금당', '토당', '일당']
def modifycalcq(calendraft, dutytypes):
  for i in holidays:
    calendraft[i][0] = 5

  yesteroff = False
  for i in calendraft:
    if calendraft[i][0] == 5 or calendraft[i][0] == 6:
      if yesteroff == True: calendraft[i][0] = 6
      yesteroff = True
    else: yesteroff = False


  for i in calendraft:
    if  calendraft[i][0] <= 3:
      calendraft[i].append(dutytypes[0])
    elif calendraft[i][0] == 4:
      calendraft[i].append(dutytypes[1])
    elif calendraft[i][0] == 5:
      calendraft[i].append(dutytypes[2])
    elif calendraft[i][0] == 6:
      calendraft[i].append(dutytypes[3])

  return calen

calencq = modifycalcq(calen, dutytypescq)
#table for operators
tablecq = maketable1(workerscq, dutytypescq, calen)



