from flare.priorityqueue import PriorityQueue
from flare.viur import BoneSelector, ModuleWidgetSelector, DisplayDelegateSelector  # Import from Flare

HandlerClassSelector = PriorityQueue()  # Used during startup to select an Wrapper-Class
actionDelegateSelector = PriorityQueue()  # Locates an action for a given module/action-name
initialHashHandler = PriorityQueue()  # Provides the handler for the initial hash given in the url
extendedSearchWidgetSelector = PriorityQueue()  # Selects a widget used to perform user-customizable searches
toplevelActionSelector = PriorityQueue()  # Top bar actions queue
loginHandlerSelector = PriorityQueue()  # Login handlers


class StartupQueue(object):
	def __init__(self):
		super(StartupQueue, self).__init__()
		self.q = []
		self.reset()

	def reset(self):
		self.isRunning = False
		self.currentElem = -1
		self.finalElem = None

	def setFinalElem(self, elem):
		assert self.finalElem is None
		assert not self.isRunning
		self.finalElem = elem

	def insertElem(self, priority, elem):
		assert not self.isRunning
		self.q.append((priority, elem))

	def run(self):
		assert not self.isRunning
		assert self.finalElem is not None
		self.isRunning = True
		self.next()

	def next(self):
		self.currentElem += 1
		if self.currentElem < len(self.q):  # This index is still valid
			cb = self.q[self.currentElem][1]
			print("Running startup callback #%s" % str(self.currentElem))
			cb()
		elif self.currentElem == len(self.q):  # We should call the final element
			self.finalElem()
			self.reset()
		else:
			raise RuntimeError("StartupQueue has no more elements to call. Someone called next() twice!")


startupQueue = StartupQueue()
